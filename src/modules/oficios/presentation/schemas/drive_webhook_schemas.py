"""
Schemas Pydantic para endpoints de Google Drive webhook.
"""

from typing import Optional
from pydantic import BaseModel, Field


class DriveWebhookRequest(BaseModel):
    """
    Request del webhook de Google Drive.

    Google Drive envía notificaciones cuando hay cambios en archivos.
    """

    file_id: str = Field(..., description="ID del archivo en Google Drive")
    change_type: str = Field(..., description="Tipo de cambio (file, folder, etc.)")
    change_time: Optional[str] = Field(None, description="Timestamp del cambio")
    folder_id: Optional[str] = Field(None, description="ID de la carpeta padre")


class DriveProcessRequest(BaseModel):
    """Request para procesamiento manual de documento."""

    drive_file_id: str = Field(..., description="ID del archivo en Google Drive a procesar")


class DriveWebhookResponse(BaseModel):
    """Response del webhook de Google Drive."""

    status: str = Field(
        ..., description="Status del procesamiento (accepted, completed, error, waiting)"
    )
    message: str = Field(..., description="Mensaje descriptivo")
    drive_file_id: str = Field(..., description="ID del archivo procesado")
    task_id: Optional[str] = Field(None, description="ID de la tarea Celery (si aplica)")
    oficio_id: Optional[int] = Field(None, description="ID del oficio creado (si aplica)")
