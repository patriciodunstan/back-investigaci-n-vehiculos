"""
Schemas para subida de documentos.

Define los schemas de request y response para el endpoint
de batch upload de documentos.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentUploadInfo(BaseModel):
    """Información de un documento subido."""

    file_id: str = Field(..., description="ID único del archivo (UUID)")
    file_name: str = Field(..., description="Nombre original del archivo")
    storage_path: str = Field(..., description="Ruta relativa donde se guardó el archivo")
    tipo_documento: Optional[str] = Field(
        None, description="Tipo detectado (OFICIO, CAV, DESCONOCIDO)"
    )
    status: str = Field(..., description="Estado del procesamiento")


class BatchUploadResponse(BaseModel):
    """Respuesta del endpoint de batch upload."""

    task_ids: List[str] = Field(..., description="IDs de las tareas Celery encoladas")
    total_files: int = Field(..., description="Total de archivos subidos")
    processed_files: List[DocumentUploadInfo] = Field(
        ..., description="Información de cada archivo procesado"
    )
    buffet_id: Optional[int] = Field(None, description="ID del buffet asociado")
    status: str = Field(..., description="Estado general del batch")
    message: str = Field(..., description="Mensaje descriptivo")
