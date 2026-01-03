"""
Modelo SQLAlchemy para Direccion.

Representa una dirección a verificar en la investigación.

Principios aplicados:
- SRP: Solo define la estructura de la tabla direcciones
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Enum,
    Boolean,
    DateTime,
    Text,
)
from sqlalchemy.orm import relationship

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import TipoDireccionEnum


class DireccionModel(Base):
    """
    Modelo de base de datos para direcciones.

    Un oficio puede tener múltiples direcciones:
    - Dirección inicial del Excel
    - Direcciones adicionales encontradas
    - Direcciones verificadas en terreno

    Attributes:
        oficio_id: FK al oficio
        direccion: Dirección completa
        comuna: Comuna
        region: Región
        tipo: Tipo de dirección
        verificada: Si fue verificada en terreno
        fecha_verificacion: Cuándo se verificó
        notas: Notas adicionales
        agregada_por_id: Usuario que agregó la dirección

    Relationships:
        oficio: Oficio al que pertenece
        agregada_por: Usuario que la agregó
    """

    __tablename__ = "direcciones"

    # Relación con Oficio
    oficio_id = Column(
        Integer,
        ForeignKey("oficios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del oficio",
    )

    # Datos de la dirección
    direccion = Column(String(500), nullable=False, comment="Dirección completa")
    comuna = Column(String(100), nullable=True, comment="Comuna")
    region = Column(String(100), nullable=True, comment="Región")
    tipo = Column(
        Enum(TipoDireccionEnum, name="tipo_direccion_enum", create_type=True),
        nullable=False,
        default=TipoDireccionEnum.DOMICILIO,
        comment="Tipo de dirección",
    )

    # Verificación
    verificada = Column(
        Boolean, default=False, nullable=False, comment="Si fue verificada en terreno"
    )
    fecha_verificacion = Column(
        DateTime(timezone=True), nullable=True, comment="Fecha y hora de verificación"
    )

    # Notas
    notas = Column(Text, nullable=True, comment="Notas adicionales")

    # Quién la agregó
    agregada_por_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del usuario que agregó la dirección",
    )

    # Relaciones
    oficio = relationship("OficioModel", back_populates="direcciones", lazy="joined")
    agregada_por = relationship(
        "UsuarioModel", back_populates="direcciones_agregadas", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<DireccionModel(id={self.id}, direccion='{self.direccion[:30]}...', verificada={self.verificada})>"
