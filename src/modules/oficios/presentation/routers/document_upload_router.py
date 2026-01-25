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

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database.session import get_db
from src.core.config import get_settings
from src.modules.oficios.presentation.schemas.document_upload_schemas import (
    BatchUploadResponse,
    DocumentUploadInfo,
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
        logger.info(f"Documento {file_id} procesado: {result.get('status')}")
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
