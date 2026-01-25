"""
Celery Task: Procesar Par de Documentos desde Local Storage.

Procesa pares de documentos (Oficio + CAV) de forma asíncrona,
combinando datos, enriqueciendo con Boostr y creando oficios.
"""

import json
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

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
)
from src.modules.oficios.application.use_cases import CreateOficioFromDocumentPairUseCase
from src.modules.oficios.application.dtos import (
    OficioExtraidoDTO,
    CAVExtraidoDTO,
    ParDocumentoDTO,
)
from src.modules.oficios.infrastructure.repositories import OficioRepository
from src.shared.infrastructure.services import get_file_storage, get_pdf_processor
from src.shared.domain.enums import (
    TipoDocumentoEnum,
    EstadoDocumentoProcesadoEnum,
)
from src.core.config import get_settings
from src.modules.oficios.domain.exceptions import NumeroOficioAlreadyExistsException


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
# async def process_document_pair_task(self, file_id: str) -> Dict[str, Any]:
#     ...


async def process_document_pair_task(file_id: str) -> Dict[str, Any]:
    """
    Task para procesar un documento desde local storage.

    Esta función puede ser envuelta en una task de Celery cuando
    Celery esté configurado en el proyecto.

    Args:
        file_id: ID único del archivo (UUID) o storage_path

    Returns:
        Dict con el resultado del procesamiento

    Raises:
        Exception: Si hay un error no recuperable
    """
    async with AsyncSessionLocal() as session:
        try:
            # 1. Buscar documento procesado por file_id o storage_path
            stmt = select(DocumentoProcesadoModel).where(DocumentoProcesadoModel.file_id == file_id)
            result = await session.execute(stmt)
            doc_procesado = result.scalar_one_or_none()

            if not doc_procesado:
                return {
                    "status": "error",
                    "message": f"Documento procesado no encontrado: {file_id}",
                    "file_id": file_id,
                }

            # 2. Leer PDF desde storage local
            storage_service = get_file_storage()
            pdf_bytes = storage_service.get_file(doc_procesado.storage_path)

            # Validar que sea PDF
            if not pdf_bytes[:4] == b"%PDF":
                return {
                    "status": "error",
                    "message": "Archivo no es PDF",
                    "file_id": file_id,
                }

            # Validar tamaño
            if len(pdf_bytes) > settings.MAX_FILE_SIZE:
                return {
                    "status": "error",
                    "message": f"Archivo muy grande: {len(pdf_bytes)} bytes",
                    "file_id": file_id,
                }

            # 3. Extraer texto
            pdf_processor = get_pdf_processor()
            texto = pdf_processor.extract_text_from_bytes(pdf_bytes)

            if not texto or len(texto.strip()) < 50:
                return {
                    "status": "error",
                    "message": "No se pudo extraer texto del PDF",
                    "file_id": file_id,
                }

            # 4. Detectar tipo de documento (si no está ya detectado)
            if doc_procesado.tipo_documento == TipoDocumentoEnum.DESCONOCIDO:
                tipo_documento = _detectar_tipo_documento(doc_procesado.file_name, texto)
                doc_procesado.tipo_documento = tipo_documento
            else:
                tipo_documento = doc_procesado.tipo_documento

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
                    "file_id": file_id,
                }

            # Actualizar datos extraídos
            doc_procesado.datos_extraidos_json = json.dumps(datos_extraidos, default=str)
            await session.flush()

            # 6. Buscar par
            detector = DocumentPairDetector(session)
            par_documento = await detector.find_pair(
                doc_procesado.file_id,
                tipo_documento,
                doc_procesado.buffet_id,
                doc_procesado.created_at,
            )

            if par_documento:
                # 7. Procesar par completo
                return await _procesar_par_completo(
                    session,
                    doc_procesado,
                    par_documento,
                    tipo_documento,
                    oficio_extraido,
                    cav_extraido,
                    pdf_bytes,
                )
            else:
                # 8. Marcar como ESPERANDO_PAR
                doc_procesado.estado = EstadoDocumentoProcesadoEnum.ESPERANDO_PAR
                await session.commit()

                return {
                    "status": "waiting",
                    "message": "Esperando par de documento",
                    "file_id": file_id,
                    "documento_procesado_id": doc_procesado.id,
                }

        except Exception as e:
            logger.error(f"Error procesando documento {file_id}: {str(e)}", exc_info=True)
            # Actualizar estado a ERROR si existe el registro
            try:
                async with AsyncSessionLocal() as error_session:
                    stmt = select(DocumentoProcesadoModel).where(
                        DocumentoProcesadoModel.file_id == file_id
                    )
                    result = await error_session.execute(stmt)
                    doc = result.scalar_one_or_none()
                    if doc:
                        doc.estado = EstadoDocumentoProcesadoEnum.ERROR
                        doc.error_mensaje = str(e)
                        await error_session.commit()
            except Exception:
                pass  # Ignorar errores al actualizar estado

            return {
                "status": "error",
                "message": str(e),
                "file_id": file_id,
            }


def _detectar_tipo_documento(nombre_archivo: str, texto: str) -> TipoDocumentoEnum:
    """Detecta el tipo de documento basándose en nombre y texto."""
    nombre_lower = nombre_archivo.lower()
    texto_lower = texto.lower()

    # Normalizar nombre (sin acentos y espacios)
    nombre_normalizado = (
        nombre_lower.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

    # Buscar keywords en nombre
    if "oficio" in nombre_normalizado or "of-" in nombre_normalizado:
        return TipoDocumentoEnum.OFICIO
    if "cav" in nombre_normalizado or "certificado" in nombre_normalizado:
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


async def _procesar_par_completo(
    session: AsyncSession,
    doc_procesado: DocumentoProcesadoModel,
    par_documento: DocumentoProcesadoModel,
    tipo_actual: TipoDocumentoEnum,
    oficio_extraido: Optional[OficioExtraidoDTO],
    cav_extraido: Optional[CAVExtraidoDTO],
    pdf_bytes: bytes,
) -> Dict[str, Any]:
    """Procesa un par completo de documentos."""
    # Leer el otro PDF desde storage local
    storage_service = get_file_storage()
    par_pdf_bytes = storage_service.get_file(par_documento.storage_path)

    # Parsear el otro documento
    pdf_processor = get_pdf_processor()
    par_texto = pdf_processor.extract_text_from_bytes(par_pdf_bytes)

    if tipo_actual == TipoDocumentoEnum.OFICIO:
        # El actual es Oficio, el par es CAV
        parser = CAVParser()
        datos_par = parser.parse(par_texto)
        cav_extraido = CAVExtraidoDTO(**datos_par)
        # Actualizar datos extraídos del par
        par_documento.datos_extraidos_json = json.dumps(datos_par, default=str)
    else:
        # El actual es CAV, el par es Oficio
        parser = OficioParser()
        datos_par = parser.parse(par_texto)
        oficio_extraido = OficioExtraidoDTO(**datos_par)
        # Actualizar datos extraídos del par
        par_documento.datos_extraidos_json = json.dumps(datos_par, default=str)

    # Crear ParDocumentoDTO
    if tipo_actual == TipoDocumentoEnum.OFICIO:
        par_dto = ParDocumentoDTO(
            file_id_oficio=doc_procesado.file_id,
            file_id_cav=par_documento.file_id,
            file_name_oficio=doc_procesado.file_name,
            file_name_cav=par_documento.file_name,
            storage_path_oficio=doc_procesado.storage_path,
            storage_path_cav=par_documento.storage_path,
            oficio_extraido=oficio_extraido,
            cav_extraido=cav_extraido,
            buffet_id=doc_procesado.buffet_id,
            pdf_bytes_oficio=pdf_bytes,
            pdf_bytes_cav=par_pdf_bytes,
        )
    else:
        par_dto = ParDocumentoDTO(
            file_id_oficio=par_documento.file_id,
            file_id_cav=doc_procesado.file_id,
            file_name_oficio=par_documento.file_name,
            file_name_cav=doc_procesado.file_name,
            storage_path_oficio=par_documento.storage_path,
            storage_path_cav=doc_procesado.storage_path,
            oficio_extraido=oficio_extraido,
            cav_extraido=cav_extraido,
            buffet_id=doc_procesado.buffet_id,
            pdf_bytes_oficio=par_pdf_bytes,
            pdf_bytes_cav=pdf_bytes,
        )

    # Crear oficio usando UseCase
    repository = OficioRepository(session)
    use_case = CreateOficioFromDocumentPairUseCase(repository)
    
    # Intentar crear oficio (puede fallar por numero de oficio duplicado)
    try:
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
            "file_id": doc_procesado.file_id,
            "par_file_id": par_documento.file_id,
        }
    except NumeroOficioAlreadyExistsException as e:
        # Actualizar estado a error en ambos documentos
        doc_procesado.estado = EstadoDocumentoProcesadoEnum.ERROR
        doc_procesado.error_mensaje = f"El número de oficio ya existe: {e.message}"
        par_documento.estado = EstadoDocumentoProcesadoEnum.ERROR
        par_documento.error_mensaje = f"El número de oficio ya existe: {e.message}"
        await session.commit()
        
        return {
            "status": "error",
            "message": f"El número de oficio '{e.numero_oficio}' ya existe en el sistema",
            "file_id": doc_procesado.file_id,
            "error_code": "OFICIO_DUPLICADO",
        }
