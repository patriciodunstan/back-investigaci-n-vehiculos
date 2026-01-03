"""
Modelo SQLAlchemy para Notificacion.

Representa una notificación enviada (email, SMS, etc).

Principios aplicados:
- SRP: Solo define la estructura de la tabla notificaciones
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Enum,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.orm import relationship

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import TipoNotificacionEnum


class NotificacionModel(Base):
    """
    Modelo de base de datos para notificaciones.

    Registra cada notificación enviada:
    - Email a receptor judicial
    - Email a buffet cliente
    - Notificaciones internas

    Attributes:
        oficio_id: FK al oficio
        tipo: Tipo de notificación
        destinatario: Email o identificador del destinatario
        asunto: Asunto del email/notificación
        contenido: Contenido/body del mensaje
        enviada: Si fue enviada exitosamente
        fecha_envio: Fecha y hora de envío
        intentos: Número de intentos de envío
        error_mensaje: Mensaje de error si falló
        metadata_json: Metadata adicional

    Relationships:
        oficio: Oficio al que pertenece
    """

    __tablename__ = "notificaciones"

    # Relación con Oficio
    oficio_id = Column(
        Integer,
        ForeignKey("oficios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del oficio",
    )

    # Tipo de notificación
    tipo = Column(
        Enum(TipoNotificacionEnum, name="tipo_notificacion_enum", create_type=True),
        nullable=False,
        comment="Tipo de notificación",
    )

    # Datos del mensaje
    destinatario = Column(
        String(255), nullable=False, comment="Email o identificador del destinatario"
    )
    asunto = Column(String(500), nullable=True, comment="Asunto del email/notificación")
    contenido = Column(Text, nullable=True, comment="Contenido del mensaje")

    # Estado de envío
    enviada = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Si fue enviada exitosamente",
    )
    fecha_envio = Column(
        DateTime(timezone=True), nullable=True, comment="Fecha y hora de envío exitoso"
    )
    intentos = Column(
        Integer, default=0, nullable=False, comment="Número de intentos de envío"
    )
    error_mensaje = Column(Text, nullable=True, comment="Mensaje de error si falló")

    # Metadata
    metadata_json = Column(Text, nullable=True, comment="Metadata adicional en JSON")

    # Relación
    oficio = relationship("OficioModel", back_populates="notificaciones", lazy="joined")

    def __repr__(self) -> str:
        return f"<NotificacionModel(id={self.id}, tipo='{self.tipo.value}', enviada={self.enviada})>"
