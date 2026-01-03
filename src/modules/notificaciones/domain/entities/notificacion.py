"""
Entidad de Dominio Notificacion.

Representa una notificacion enviada.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.enums import TipoNotificacionEnum


@dataclass
class Notificacion(BaseEntity):
    """
    Entidad que representa una notificacion.

    Attributes:
        oficio_id: ID del oficio relacionado
        tipo: Tipo de notificacion
        destinatario: Email o identificador del destinatario
        asunto: Asunto del mensaje
        contenido: Contenido del mensaje
        enviada: Si fue enviada exitosamente
        fecha_envio: Fecha y hora de envio
        intentos: Numero de intentos de envio
        error_mensaje: Mensaje de error si fallo
        metadata_json: Metadata adicional
    """

    oficio_id: int = 0
    tipo: TipoNotificacionEnum = TipoNotificacionEnum.NOTIFICACION_INTERNA
    destinatario: str = ""
    asunto: Optional[str] = None
    contenido: Optional[str] = None
    enviada: bool = False
    fecha_envio: Optional[datetime] = None
    intentos: int = 0
    error_mensaje: Optional[str] = None
    metadata_json: Optional[str] = None

    @classmethod
    def crear_email(
        cls,
        oficio_id: int,
        tipo: TipoNotificacionEnum,
        destinatario: str,
        asunto: str,
        contenido: str,
    ) -> "Notificacion":
        """Crea una notificacion de email."""
        return cls(
            oficio_id=oficio_id,
            tipo=tipo,
            destinatario=destinatario,
            asunto=asunto,
            contenido=contenido,
        )

    def marcar_enviada(self) -> None:
        """Marca la notificacion como enviada."""
        self.enviada = True
        self.fecha_envio = datetime.utcnow()
        self.marcar_actualizado()

    def registrar_error(self, mensaje: str) -> None:
        """Registra un error de envio."""
        self.intentos += 1
        self.error_mensaje = mensaje
        self.marcar_actualizado()

    def reintentar(self) -> bool:
        """Verifica si se puede reintentar el envio."""
        return not self.enviada and self.intentos < 3
