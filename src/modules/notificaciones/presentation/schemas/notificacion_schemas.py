"""
Schemas Pydantic para la API de notificaciones.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from src.shared.domain.enums import TipoNotificacionEnum


class CreateNotificacionRequest(BaseModel):
    """Schema para crear notificacion."""

    tipo: TipoNotificacionEnum = Field(default=TipoNotificacionEnum.BUFFET)
    destinatario: str = Field(..., min_length=3, max_length=255)
    asunto: Optional[str] = Field(None, max_length=500)
    contenido: Optional[str] = Field(None, max_length=5000)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tipo": "buffet",
                "destinatario": "cliente@ejemplo.cl",
                "asunto": "Actualizacion de caso",
                "contenido": "Se ha encontrado el vehiculo...",
            }
        }
    )


class NotificacionResponse(BaseModel):
    """Schema de respuesta de notificacion."""

    id: int
    oficio_id: int
    tipo: str
    destinatario: str
    asunto: Optional[str]
    contenido: Optional[str]
    enviada: bool
    fecha_envio: Optional[datetime]
    intentos: int
    error_mensaje: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificacionListResponse(BaseModel):
    """Schema de lista de notificaciones."""

    oficio_id: int
    items: List[NotificacionResponse]
    total: int
