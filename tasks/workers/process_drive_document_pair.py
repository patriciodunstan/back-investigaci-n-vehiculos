"""
Celery Task: Procesar Par de Documentos desde Google Drive.

Procesa pares de documentos (Oficio + CAV) de forma asíncrona,
combinando datos, enriqueciendo con Boostr y creando oficios.
"""

import json
import logging
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.shared.infrastructure.database.session import AsyncSessionLocal
from src.modules.oficios.infrastructure.models.documento_procesado_model import (
    DocumentoProcesadoModel,
)
from src.modules.oficios.infrastructure.services import (
    OficioParser,
    CAVParser,
    DocumentPairDetector,
    get_buffet_mapper,
)
from src.modules.oficios.application.use_cases import CreateOficioFromDocumentPairUseCase
from src.modules.oficios.application.dtos import (
    OficioExtraidoDTO,
    CAVExtraidoDTO,
    ParDocumentoDTO,
)
from src.modules.oficios.infrastructure.repositories import OficioRepository
from src.shared.infrastructure.external_apis.google_drive import get_google_drive_client
from src.shared.infrastructure.services.pdf_processor import get_pdf_processor
from src.shared.domain.enums import (
    TipoDocumentoEnum,
    EstadoDocumentoProcesadoEnum,
)
from src.core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


# NOTE: Esta tarea requiere que Celery esté configurado.
# Para usar esta tarea, necesitas:
# 1. Crear celery_app en tasks/celery_app.py
# 2. Importar celery_app aquí
# 3. Decorar la función con @celery_app.task()

# Ejemplo de cómo debería verse:
# from tasks.celery_app import celery_app
#
# @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
# async def process_drive_document_pair(self, drive_file_id: str) -> Dict[str, Any]:
#     ...


async def process_drive_document_pair_task(drive_file_id: str) -> Dict[str, Any]:
    """
    Task para procesar un documento desde Google Drive.

    Esta función puede ser envuelta en una task de Celery cuando
    Celery esté configurado en el proyecto.

    Args:
        drive_file_id: ID del archivo en Google Drive

    Returns:
        Dict con el resultado del procesamiento

    Raises:
        Exception: Si hay un error no recuperable
    """
    async with AsyncSessionLocal() as session:
        try:
            # 1. Obtener metadatos del archivo desde Google Drive
            drive_client = get_google_drive_client()
            file_metadata = await drive_client.get_file_metadata(drive_file_id)

            # Validar que sea PDF
            if file_metadata.mime_type and "pdf" not in file_metadata.mime_type.lower():
                return {
                    "status": "error",
                    "message": f"Archivo no es PDF: {file_metadata.mime_type}",
                    "drive_file_id": drive_file_id,
                }

            # Validar tamaño
            if (
                file_metadata.size_bytes
                and file_metadata.size_bytes > settings.PDF_MAX_SIZE_MB * 1024 * 1024
            ):
                return {
                    "status": "error",
                    "message": f"Archivo muy grande: {file_metadata.size_bytes} bytes",
                    "drive_file_id": drive_file_id,
                }

            # 2. Descargar PDF
            pdf_bytes = await drive_client.download_file(drive_file_id)

            # 3. Extraer texto
            pdf_processor = get_pdf_processor()
            texto = pdf_processor.extract_text_from_bytes(pdf_bytes)

            if not texto or len(texto.strip()) < 50:
                return {
                    "status": "error",
                    "message": "No se pudo extraer texto del PDF",
                    "drive_file_id": drive_file_id,
                }

            # 4. Detectar tipo de documento
            tipo_documento = _detectar_tipo_documento(file_metadata.name, texto)

            # 5. Parsear documento
            if tipo_documento == TipoDocumentoEnum.OFICIO:
                parser = OficioParser()
                datos_extraidos = parser.parse(texto)
                oficio_extraido = OficioExtraidoDTO(**datos_extraidos)
                cav_extraido = None
            elif tipo_documento == TipoDocumentoEnum.CAV:
                parser = CAVParser()
                datos_extraidos = parser.parse(texto)
                cav_extraido = CAVExtraidoDTO(**datos_extraidos)
                oficio_extraido = None
            else:
                return {
                    "status": "error",
                    "message": "No se pudo identificar el tipo de documento",
                    "drive_file_id": drive_file_id,
                }

            # 6. Obtener buffet_id
            buffet_mapper = get_buffet_mapper()
            buffet_id = buffet_mapper.get_buffet_id(
                file_metadata.parents[0] if file_metadata.parents else ""
            )

            # 7. Crear o actualizar registro en DocumentoProcesadoModel
            doc_procesado = await _get_or_create_documento_procesado(
                session,
                drive_file_id,
                file_metadata.name,
                file_metadata.parents[0] if file_metadata.parents else "",
                tipo_documento,
                datos_extraidos,
            )

            # 8. Buscar par
            detector = DocumentPairDetector(session)
            par_documento = await detector.find_pair(
                drive_file_id,
                tipo_documento,
                file_metadata.parents[0] if file_metadata.parents else "",
                file_metadata.created_time,
            )

            if par_documento:
                # 9. Procesar par completo
                return await _procesar_par_completo(
                    session,
                    doc_procesado,
                    par_documento,
                    tipo_documento,
                    oficio_extraido,
                    cav_extraido,
                    file_metadata,
                    pdf_bytes,
                    buffet_id,
                )
            else:
                # 10. Marcar como ESPERANDO_PAR
                doc_procesado.estado = EstadoDocumentoProcesadoEnum.ESPERANDO_PAR
                await session.commit()

                return {
                    "status": "waiting",
                    "message": "Esperando par de documento",
                    "drive_file_id": drive_file_id,
                    "documento_procesado_id": doc_procesado.id,
                }

        except Exception as e:
            logger.error(f"Error procesando documento {drive_file_id}: {str(e)}", exc_info=True)
            # Actualizar estado a ERROR si existe el registro
            try:
                async with AsyncSessionLocal() as error_session:
                    stmt = select(DocumentoProcesadoModel).where(
                        DocumentoProcesadoModel.drive_file_id == drive_file_id
                    )
                    result = await error_session.execute(stmt)
                    # unique() es requerido porque DocumentoProcesadoModel tiene relaciones con lazy="joined"
                    doc = result.unique().scalar_one_or_none()
                    if doc:
                        doc.estado = EstadoDocumentoProcesadoEnum.ERROR
                        doc.error_mensaje = str(e)
                        await error_session.commit()
            except Exception:
                pass  # Ignorar errores al actualizar estado

            return {
                "status": "error",
                "message": str(e),
                "drive_file_id": drive_file_id,
            }


def _detectar_tipo_documento(nombre_archivo: str, texto: str) -> TipoDocumentoEnum:
    """Detecta el tipo de documento basándose en nombre y texto."""
    nombre_lower = nombre_archivo.lower()
    texto_lower = texto.lower()

    # Buscar keywords en nombre
    if "oficio" in nombre_lower or "of-" in nombre_lower:
        return TipoDocumentoEnum.OFICIO
    if "cav" in nombre_lower or "certificado" in nombre_lower:
        return TipoDocumentoEnum.CAV

    # Buscar keywords en texto
    if any(keyword in texto_lower for keyword in ["oficio", "rol", "juzgado"]):
        return TipoDocumentoEnum.OFICIO
    if any(
        keyword in texto_lower
        for keyword in ["certificado de inscripción", "patente", "marca", "modelo"]
    ):
        return TipoDocumentoEnum.CAV

    return TipoDocumentoEnum.DESCONOCIDO


async def _get_or_create_documento_procesado(
    session: AsyncSession,
    drive_file_id: str,
    drive_file_name: str,
    drive_folder_id: str,
    tipo_documento: TipoDocumentoEnum,
    datos_extraidos: Dict[str, Any],
) -> DocumentoProcesadoModel:
    """Obtiene o crea un registro de DocumentoProcesadoModel."""

    stmt = select(DocumentoProcesadoModel).where(
        DocumentoProcesadoModel.drive_file_id == drive_file_id
    )
    result = await session.execute(stmt)
    # unique() es requerido porque DocumentoProcesadoModel tiene relaciones con lazy="joined"
    doc = result.unique().scalar_one_or_none()

    if doc:
        # Actualizar
        doc.tipo_documento = tipo_documento
        doc.datos_extraidos_json = json.dumps(datos_extraidos, default=str)
        doc.estado = EstadoDocumentoProcesadoEnum.PROCESANDO
    else:
        # Crear nuevo
        doc = DocumentoProcesadoModel(
            drive_file_id=drive_file_id,
            drive_file_name=drive_file_name,
            drive_folder_id=drive_folder_id,
            tipo_documento=tipo_documento,
            estado=EstadoDocumentoProcesadoEnum.PROCESANDO,
            datos_extraidos_json=json.dumps(datos_extraidos, default=str),
        )
        session.add(doc)

    await session.flush()
    return doc


async def _procesar_par_completo(
    session: AsyncSession,
    doc_procesado: DocumentoProcesadoModel,
    par_documento: DocumentoProcesadoModel,
    tipo_actual: TipoDocumentoEnum,
    oficio_extraido: Optional[OficioExtraidoDTO],
    cav_extraido: Optional[CAVExtraidoDTO],
    file_metadata,
    pdf_bytes: bytes,
    buffet_id: Optional[int],
) -> Dict[str, Any]:
    """Procesa un par completo de documentos."""
    # Descargar el otro PDF
    drive_client = get_google_drive_client()
    par_pdf_bytes = await drive_client.download_file(par_documento.drive_file_id)

    # Parsear el otro documento
    pdf_processor = get_pdf_processor()
    par_texto = pdf_processor.extract_text_from_bytes(par_pdf_bytes)

    if tipo_actual == TipoDocumentoEnum.OFICIO:
        # El actual es Oficio, el par es CAV
        parser = CAVParser()
        datos_par = parser.parse(par_texto)
        cav_extraido = CAVExtraidoDTO(**datos_par)
    else:
        # El actual es CAV, el par es Oficio
        parser = OficioParser()
        datos_par = parser.parse(par_texto)
        oficio_extraido = OficioExtraidoDTO(**datos_par)

    # Crear ParDocumentoDTO
    if tipo_actual == TipoDocumentoEnum.OFICIO:
        par_dto = ParDocumentoDTO(
            drive_file_id_oficio=doc_procesado.drive_file_id,
            drive_file_id_cav=par_documento.drive_file_id,
            drive_file_name_oficio=doc_procesado.drive_file_name,
            drive_file_name_cav=par_documento.drive_file_name,
            drive_folder_id=doc_procesado.drive_folder_id,
            oficio_extraido=oficio_extraido,
            cav_extraido=cav_extraido,
            buffet_id=buffet_id,
            pdf_bytes_oficio=pdf_bytes,
            pdf_bytes_cav=par_pdf_bytes,
        )
    else:
        par_dto = ParDocumentoDTO(
            drive_file_id_oficio=par_documento.drive_file_id,
            drive_file_id_cav=doc_procesado.drive_file_id,
            drive_file_name_oficio=par_documento.drive_file_name,
            drive_file_name_cav=doc_procesado.drive_file_name,
            drive_folder_id=doc_procesado.drive_folder_id,
            oficio_extraido=oficio_extraido,
            cav_extraido=cav_extraido,
            buffet_id=buffet_id,
            pdf_bytes_oficio=par_pdf_bytes,
            pdf_bytes_cav=pdf_bytes,
        )

    # Crear oficio usando UseCase
    repository = OficioRepository(session)
    use_case = CreateOficioFromDocumentPairUseCase(repository)
    oficio_response = await use_case.execute(par_dto)

    # Actualizar estados
    doc_procesado.estado = EstadoDocumentoProcesadoEnum.COMPLETADO
    doc_procesado.oficio_id = oficio_response.id
    doc_procesado.par_documento_id = par_documento.id

    par_documento.estado = EstadoDocumentoProcesadoEnum.COMPLETADO
    par_documento.oficio_id = oficio_response.id
    par_documento.par_documento_id = doc_procesado.id

    await session.commit()

    return {
        "status": "completed",
        "message": "Par procesado exitosamente",
        "oficio_id": oficio_response.id,
        "drive_file_id": doc_procesado.drive_file_id,
        "par_drive_file_id": par_documento.drive_file_id,
    }
