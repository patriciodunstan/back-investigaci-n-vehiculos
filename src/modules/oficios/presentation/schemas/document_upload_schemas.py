"""
Schemas para subida de documentos.

Define los schemas de request y response para el endpoint
de batch upload de documentos.
"""

from datetime import datetime
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


# =============================================================================
# SCHEMAS PARA CONSULTA DE ESTADO
# =============================================================================


class DocumentStatusInfo(BaseModel):
    """Estado detallado de un documento procesado."""

    file_id: str = Field(..., description="ID único del archivo")
    file_name: str = Field(..., description="Nombre original del archivo")
    tipo_documento: Optional[str] = Field(None, description="Tipo de documento (OFICIO, CAV)")
    estado: str = Field(
        ..., 
        description="Estado actual: pendiente, esperando_par, procesando, completado, error, duplicado"
    )
    error_mensaje: Optional[str] = Field(None, description="Mensaje de error si aplica")
    oficio_id: Optional[int] = Field(None, description="ID del oficio creado (si completado)")
    numero_oficio: Optional[str] = Field(None, description="Número del oficio (si existe)")
    par_file_id: Optional[str] = Field(None, description="ID del documento par relacionado")
    created_at: datetime = Field(..., description="Fecha de subida")
    updated_at: Optional[datetime] = Field(None, description="Última actualización")

    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    """Respuesta de consulta de estado de documentos."""

    documentos: List[DocumentStatusInfo] = Field(..., description="Lista de documentos con su estado")
    total: int = Field(..., description="Total de documentos consultados")
    
    # Resumen por estado
    resumen: dict = Field(
        ..., 
        description="Conteo por estado: {completado: N, duplicado: N, error: N, ...}"
    )


class DocumentStatusByOficioResponse(BaseModel):
    """Estado de documentos agrupados por número de oficio."""

    numero_oficio: str = Field(..., description="Número del oficio")
    estado: str = Field(..., description="Estado del procesamiento")
    oficio_id: Optional[int] = Field(None, description="ID del oficio en el sistema (si existe)")
    mensaje: str = Field(..., description="Mensaje descriptivo del estado")
    documentos: List[DocumentStatusInfo] = Field(..., description="Documentos relacionados")
