"""
DTOs para el modulo Notificaciones.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from src.shared.domain.enums import TipoNotificacionEnum


@dataclass(frozen=True)
class CreateNotificacionDTO:
    """DTO para crear notificacion."""

    oficio_id: int
    tipo: TipoNotificacionEnum
    destinatario: str
    asunto: Optional[str] = None
    contenido: Optional[str] = None


@dataclass
class NotificacionResponseDTO:
    """DTO de respuesta de notificacion."""

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
