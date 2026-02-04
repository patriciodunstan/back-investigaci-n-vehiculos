"""
Router para subida de documentos (batch upload).

Permite a los clientes subir múltiples pares de documentos (Oficio + CAV)
en batch para procesamiento automático.
"""

import logging
import json
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database.session import get_db
from src.core.config import get_settings
from sqlalchemy import select, func

from src.modules.oficios.presentation.schemas.document_upload_schemas import (
    BatchUploadResponse,
    DocumentUploadInfo,
    DocumentStatusInfo,
    DocumentStatusResponse,
)
from src.modules.oficios.infrastructure.models.documento_procesado_model import (
    DocumentoProcesadoModel,
)
from src.modules.oficios.infrastructure.services import DocumentPairDetector
from src.modules.usuarios.presentation.routers import get_current_user
from src.modules.usuarios.presentation.schemas import UserResponse
from src.shared.infrastructure.services import get_file_storage, get_pdf_processor
from src.shared.domain.enums import TipoDocumentoEnum, EstadoDocumentoProcesadoEnum


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/oficios/documents", tags=["Documentos"])
settings = get_settings()


def get_storage_service():
    """Dependency para obtener el servicio de almacenamiento."""
    return get_file_storage()


async def _process_document_in_background(file_id: str) -> None:
    """Procesa un documento en background."""
    from tasks.workers.process_document_pair import process_document_pair_task

    try:
        result = await process_document_pair_task(file_id)
        status = result.get('status')
        
        if status == "duplicated":
            # Oficio ya existía - informar claramente
            numero_oficio = result.get('numero_oficio', 'desconocido')
            logger.info(
                f"Documento {file_id}: OMITIDO - El oficio '{numero_oficio}' ya existe en el sistema"
            )
        elif status == "completed":
            oficio_id = result.get('oficio_id')
            logger.info(f"Documento {file_id}: COMPLETADO - Oficio creado (ID: {oficio_id})")
        elif status == "waiting":
            logger.info(f"Documento {file_id}: ESPERANDO PAR - Aguardando documento complementario")
        elif status == "error":
            error_msg = result.get('message', 'Error desconocido')
            logger.warning(f"Documento {file_id}: ERROR - {error_msg}")
        else:
            logger.info(f"Documento {file_id} procesado: {status}")
            
    except Exception as e:
        logger.error(f"Error procesando documento {file_id}: {e}", exc_info=True)


@router.post(
    "/upload-batch",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Subida masiva de documentos",
    description="Sube múltiples documentos PDF (Oficio + CAV) para procesamiento automático. "
    "El sistema detecta automáticamente el tipo de documento y los empareja.",
)
async def upload_batch(
    files: List[UploadFile] = File(..., description="Archivos PDF a procesar"),
    buffet_id: Optional[int] = Form(None, description="ID del buffet asociado (opcional)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    storage_service=Depends(get_storage_service),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> BatchUploadResponse:
    """
    Sube múltiples documentos PDF para procesamiento.

    Acepta batch de archivos (hasta 200), los valida, guarda en storage local,
    crea registros en DocumentoProcesadoModel y encola tareas Celery para procesamiento.

    Args:
        files: Lista de archivos PDF (hasta 200)
        buffet_id: ID del buffet asociado (opcional)
        db: Sesión de base de datos
        current_user: Usuario autenticado
        storage_service: Servicio de almacenamiento

    Returns:
        BatchUploadResponse con información de los archivos procesados
    """
    # Validar número máximo de archivos
    MAX_BATCH_SIZE = 200
    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Máximo {MAX_BATCH_SIZE} archivos por batch. Recibidos: {len(files)}",
        )

    if len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe subir al menos un archivo",
        )

    processed_files: List[DocumentUploadInfo] = []
    task_ids: List[str] = []
    pdf_processor = get_pdf_processor()

    try:
        for file in files:
            try:
                # Validar tipo de archivo
                if file.content_type not in settings.ALLOWED_FILE_TYPES:
                    processed_files.append(
                        DocumentUploadInfo(
                            file_id="",
                            file_name=file.filename or "unknown",
                            storage_path="",
                            tipo_documento=None,
                            status="error",
                        )
                    )
                    logger.warning(
                        f"Tipo de archivo no permitido: {file.content_type} "
                        f"para {file.filename}"
                    )
                    continue

                # Leer contenido del archivo
                content = await file.read()

                # Validar tamaño
                if len(content) > settings.MAX_FILE_SIZE:
                    processed_files.append(
                        DocumentUploadInfo(
                            file_id="",
                            file_name=file.filename or "unknown",
                            storage_path="",
                            tipo_documento=None,
                            status="error",
                        )
                    )
                    logger.warning(f"Archivo muy grande: {len(content)} bytes para {file.filename}")
                    continue

                # Validar que sea PDF (primeros bytes)
                if not content[:4] == b"%PDF":
                    processed_files.append(
                        DocumentUploadInfo(
                            file_id="",
                            file_name=file.filename or "unknown",
                            storage_path="",
                            tipo_documento=None,
                            status="error",
                        )
                    )
                    logger.warning(f"Archivo no es PDF: {file.filename}")
                    continue

                # Guardar archivo en storage local
                file_id = str(uuid.uuid4()).replace("-", "")
                storage_path = storage_service.save_file(content, file.filename or "documento.pdf")

                # Extraer texto para detectar tipo
                texto = pdf_processor.extract_text_from_bytes(content)
                tipo_documento = _detectar_tipo_documento(file.filename or "unknown", texto)

                # Crear registro en DocumentoProcesadoModel
                doc_procesado = DocumentoProcesadoModel(
                    file_id=file_id,
                    file_name=file.filename or "documento.pdf",
                    storage_path=storage_path,
                    tipo_documento=tipo_documento,
                    estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
                    buffet_id=buffet_id,
                    datos_extraidos_json=None,  # Se llenará después en el task
                )
                db.add(doc_procesado)
                await db.flush()

                # Crear task_id único para tracking
                task_id = f"{file_id}_{datetime.utcnow().timestamp()}"
                task_ids.append(task_id)

                # Disparar procesamiento en background
                background_tasks.add_task(_process_document_in_background, file_id)
                logger.info(f"Documento {file_id} guardado, procesamiento iniciado en background")

                processed_files.append(
                    DocumentUploadInfo(
                        file_id=file_id,
                        file_name=file.filename or "documento.pdf",
                        storage_path=storage_path,
                        tipo_documento=tipo_documento.value if tipo_documento else None,
                        status="processing",
                    )
                )

            except Exception as e:
                logger.error(f"Error procesando archivo {file.filename}: {e}", exc_info=True)
                processed_files.append(
                    DocumentUploadInfo(
                        file_id="",
                        file_name=file.filename or "unknown",
                        storage_path="",
                        tipo_documento=None,
                        status="error",
                    )
                )

        # Commit todas las creaciones
        await db.commit()

        return BatchUploadResponse(
            task_ids=task_ids,
            total_files=len(files),
            processed_files=processed_files,
            buffet_id=buffet_id,
            status="accepted",
            message=f"{len(processed_files)} archivos subidos y en proceso",
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error en batch upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando batch: {str(e)}",
        )


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


# =============================================================================
# ENDPOINTS DE CONSULTA DE ESTADO
# =============================================================================


@router.get(
    "/status",
    response_model=DocumentStatusResponse,
    summary="Consultar estado de documentos",
    description="Consulta el estado de procesamiento de documentos por sus file_ids. "
    "Permite al frontend conocer el resultado real del procesamiento.",
)
async def get_documents_status(
    file_ids: str = Query(..., description="IDs de archivos separados por coma (ej: abc123,def456)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> DocumentStatusResponse:
    """
    Consulta el estado de procesamiento de uno o más documentos.

    Este endpoint permite al frontend hacer polling para conocer el estado
    real de los documentos después de subirlos.

    Args:
        file_ids: Lista de file_ids separados por coma
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        DocumentStatusResponse con el estado de cada documento y resumen
    """
    # Parsear file_ids
    ids_list = [fid.strip() for fid in file_ids.split(",") if fid.strip()]
    
    if not ids_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un file_id",
        )
    
    if len(ids_list) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 100 file_ids por consulta",
        )

    # Consultar documentos
    stmt = select(DocumentoProcesadoModel).where(
        DocumentoProcesadoModel.file_id.in_(ids_list)
    )
    result = await db.execute(stmt)
    documentos = list(result.unique().scalars().all())

    # Construir respuesta
    documentos_info: List[DocumentStatusInfo] = []
    resumen: dict = {
        "pendiente": 0,
        "esperando_par": 0,
        "procesando": 0,
        "completado": 0,
        "error": 0,
        "duplicado": 0,
    }

    for doc in documentos:
        # Obtener número de oficio si existe
        numero_oficio = None
        if doc.datos_extraidos_json:
            try:
                datos = json.loads(doc.datos_extraidos_json)
                numero_oficio = datos.get("numero_oficio")
            except (json.JSONDecodeError, TypeError):
                pass

        documentos_info.append(
            DocumentStatusInfo(
                file_id=doc.file_id,
                file_name=doc.file_name,
                tipo_documento=doc.tipo_documento.value if doc.tipo_documento else None,
                estado=doc.estado.value,
                error_mensaje=doc.error_mensaje,
                oficio_id=doc.oficio_id,
                numero_oficio=numero_oficio,
                par_file_id=None,  # TODO: obtener del par si existe
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
        )
        
        # Actualizar resumen
        estado_key = doc.estado.value
        if estado_key in resumen:
            resumen[estado_key] += 1

    return DocumentStatusResponse(
        documentos=documentos_info,
        total=len(documentos_info),
        resumen=resumen,
    )


@router.get(
    "/status/recent",
    response_model=DocumentStatusResponse,
    summary="Documentos recientes del usuario",
    description="Obtiene los documentos procesados más recientes del buffet del usuario.",
)
async def get_recent_documents_status(
    limit: int = Query(20, ge=1, le=100, description="Máximo de documentos a retornar"),
    buffet_id: Optional[int] = Query(None, description="Filtrar por buffet (admin puede ver todos)"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> DocumentStatusResponse:
    """
    Obtiene los documentos procesados más recientes.

    Si el usuario es cliente, solo ve documentos de su buffet.
    Si es admin/investigador puede filtrar por buffet o ver todos.

    Args:
        limit: Máximo de documentos a retornar
        buffet_id: Filtrar por buffet (opcional)
        estado: Filtrar por estado (opcional)
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        DocumentStatusResponse con documentos recientes
    """
    # Construir query base
    stmt = select(DocumentoProcesadoModel)
    
    # Filtrar por buffet según rol
    if current_user.rol == "cliente" and current_user.buffet_id:
        stmt = stmt.where(DocumentoProcesadoModel.buffet_id == current_user.buffet_id)
    elif buffet_id:
        stmt = stmt.where(DocumentoProcesadoModel.buffet_id == buffet_id)
    
    # Filtrar por estado si se especifica
    if estado:
        try:
            estado_enum = EstadoDocumentoProcesadoEnum(estado)
            stmt = stmt.where(DocumentoProcesadoModel.estado == estado_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido: {estado}. Valores válidos: pendiente, esperando_par, procesando, completado, error, duplicado",
            )
    
    # Ordenar por fecha y limitar
    stmt = stmt.order_by(DocumentoProcesadoModel.created_at.desc()).limit(limit)
    
    result = await db.execute(stmt)
    documentos = list(result.unique().scalars().all())

    # Construir respuesta (similar al endpoint anterior)
    documentos_info: List[DocumentStatusInfo] = []
    resumen: dict = {
        "pendiente": 0,
        "esperando_par": 0,
        "procesando": 0,
        "completado": 0,
        "error": 0,
        "duplicado": 0,
    }

    for doc in documentos:
        numero_oficio = None
        if doc.datos_extraidos_json:
            try:
                datos = json.loads(doc.datos_extraidos_json)
                numero_oficio = datos.get("numero_oficio")
            except (json.JSONDecodeError, TypeError):
                pass

        documentos_info.append(
            DocumentStatusInfo(
                file_id=doc.file_id,
                file_name=doc.file_name,
                tipo_documento=doc.tipo_documento.value if doc.tipo_documento else None,
                estado=doc.estado.value,
                error_mensaje=doc.error_mensaje,
                oficio_id=doc.oficio_id,
                numero_oficio=numero_oficio,
                par_file_id=None,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
        )
        
        estado_key = doc.estado.value
        if estado_key in resumen:
            resumen[estado_key] += 1

    return DocumentStatusResponse(
        documentos=documentos_info,
        total=len(documentos_info),
        resumen=resumen,
    )
