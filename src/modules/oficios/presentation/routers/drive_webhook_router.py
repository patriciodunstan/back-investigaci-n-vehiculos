"""
Router para webhooks de Google Drive.

Recibe notificaciones de Google Drive cuando se suben archivos
y procesa documentos para crear oficios automáticamente.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database.session import get_db
from src.core.config import get_settings
from src.modules.oficios.presentation.schemas.drive_webhook_schemas import (
    DriveWebhookRequest,
    DriveProcessRequest,
    DriveWebhookResponse,
)
from tasks.workers.process_drive_document_pair import process_drive_document_pair_task
# DISABLED: Google Drive integration removed
# from tasks.workers.process_drive_document_pair import process_drive_document_pair_task


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/oficios/drive", tags=["Google Drive"])


@router.post(
    "/webhook",
    response_model=DriveWebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Webhook de Google Drive",
    description="Recibe notificaciones de Google Drive cuando se sube un archivo PDF.",
)
async def drive_webhook(
    request: DriveWebhookRequest,
    db: AsyncSession = Depends(get_db),
) -> DriveWebhookResponse:
    """
    Endpoint para recibir webhooks de Google Drive.

    Google Drive envía notificaciones cuando se suben archivos nuevos.
    Este endpoint valida la notificación y encola una tarea para procesar
    el documento.

    Args:
        request: Request del webhook con información del archivo
        db: Sesión de base de datos

    Returns:
        DriveWebhookResponse con el estado del procesamiento
    """
    settings = get_settings()

    # Validar que Google Drive esté habilitado
    if not settings.GOOGLE_DRIVE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Drive integration está deshabilitada",
        )

    # TODO: Validar signature del webhook (HMAC)
    # Por ahora, se acepta cualquier request
    # En producción, se debe validar la signature de Google Drive

    # Validar que sea un cambio de archivo
    if request.change_type != "file":
        return DriveWebhookResponse(
            status="ignored",
            message=f"Tipo de cambio no procesado: {request.change_type}",
            drive_file_id=request.file_id,
        )

    # Encolar tarea Celery para procesar
    # NOTE: Cuando Celery esté configurado, usar:
    # from tasks.workers.process_drive_document_pair import process_drive_document_pair_task
    # task = process_drive_document_pair_task.delay(request.file_id)

    # Por ahora, ejecutar de forma síncrona (para testing)
    try:
        result = await process_drive_document_pair_task(request.file_id)
        return DriveWebhookResponse(
            status=result.get("status", "accepted"),
            message=result.get("message", "Documento encolado para procesamiento"),
            drive_file_id=request.file_id,
            task_id=None,  # Cuando Celery esté configurado, usar task.id
            oficio_id=result.get("oficio_id"),
        )
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando documento: {str(e)}",
        )


@router.post(
    "/process",
    response_model=DriveWebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Procesamiento manual de documento",
    description="Procesa un documento de Google Drive manualmente (para testing).",
)
async def process_document_manual(
    request: DriveProcessRequest,
    db: AsyncSession = Depends(get_db),
) -> DriveWebhookResponse:
    """
    Endpoint para procesar un documento manualmente.

    Útil para testing o reprocesamiento de documentos.

    Args:
        request: Request con drive_file_id a procesar
        db: Sesión de base de datos

    Returns:
        DriveWebhookResponse con el resultado
    """
    settings = get_settings()

    if not settings.GOOGLE_DRIVE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Drive integration está deshabilitada",
        )

    try:
        result = await process_drive_document_pair_task(request.drive_file_id)
        return DriveWebhookResponse(
            status=result.get("status", "accepted"),
            message=result.get("message", "Documento procesado"),
            drive_file_id=request.drive_file_id,
            task_id=None,
            oficio_id=result.get("oficio_id"),
        )
    except Exception as e:
        logger.error(f"Error procesando documento manualmente: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando documento: {str(e)}",
        )
