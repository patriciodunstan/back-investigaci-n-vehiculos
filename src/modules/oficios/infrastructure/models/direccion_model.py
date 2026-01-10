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
from src.shared.domain.enums import TipoDireccionEnum, ResultadoVerificacionEnum


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
        resultado_verificacion: Resultado de la última verificación
        fecha_verificacion: Cuándo se verificó
        verificada_por_id: Usuario que realizó la verificación
        cantidad_visitas: Número de veces que se ha visitado
        notas: Notas adicionales
        agregada_por_id: Usuario que agregó la dirección

    Relationships:
        oficio: Oficio al que pertenece
        agregada_por: Usuario que la agregó
        verificada_por: Usuario que la verificó
        visitas: Historial de visitas a esta dirección
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
    resultado_verificacion = Column(
        Enum(ResultadoVerificacionEnum, name="resultado_verificacion_enum", create_type=True),
        nullable=False,
        default=ResultadoVerificacionEnum.PENDIENTE,
        comment="Resultado de la última verificación",
    )
    fecha_verificacion = Column(
        DateTime(timezone=True), nullable=True, comment="Fecha y hora de última verificación"
    )
    verificada_por_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del usuario que realizó la verificación",
    )
    cantidad_visitas = Column(
        Integer, default=0, nullable=False, comment="Número de visitas realizadas"
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
        "UsuarioModel",
        foreign_keys=[agregada_por_id],
        back_populates="direcciones_agregadas",
        lazy="joined",
    )
    verificada_por = relationship(
        "UsuarioModel",
        foreign_keys=[verificada_por_id],
        back_populates="direcciones_verificadas",
        lazy="joined",
    )
    visitas = relationship(
        "VisitaDireccionModel",
        back_populates="direccion",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<DireccionModel(id={self.id}, direccion='{self.direccion[:30]}...', resultado={self.resultado_verificacion.value})>"


class VisitaDireccionModel(Base):
    """
    Modelo para registrar el historial de visitas a una dirección.

    Cada vez que un investigador visita una dirección, se registra aquí.
    Esto permite tener un historial completo de intentos.

    Attributes:
        direccion_id: FK a la dirección
        investigador_id: Usuario que realizó la visita
        fecha_visita: Fecha y hora de la visita
        resultado: Resultado de esta visita específica
        notas: Notas de la visita
        latitud: Coordenada de ubicación (opcional)
        longitud: Coordenada de ubicación (opcional)
    """

    __tablename__ = "visitas_direcciones"

    # Relación con Dirección
    direccion_id = Column(
        Integer,
        ForeignKey("direcciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la dirección visitada",
    )

    # Quién visitó
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del investigador que visitó",
    )

    # Datos de la visita
    fecha_visita = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha y hora de la visita",
    )
    resultado = Column(
        Enum(ResultadoVerificacionEnum, name="resultado_verificacion_enum", create_type=False),
        nullable=False,
        comment="Resultado de esta visita",
    )
    notas = Column(Text, nullable=True, comment="Notas de la visita")

    # Ubicación GPS (opcional)
    latitud = Column(String(20), nullable=True, comment="Latitud GPS")
    longitud = Column(String(20), nullable=True, comment="Longitud GPS")

    # Relaciones
    direccion = relationship("DireccionModel", back_populates="visitas", lazy="joined")
    investigador = relationship(
        "UsuarioModel",
        back_populates="visitas_realizadas",
        lazy="joined",
        foreign_keys=[usuario_id],
    )

    def __repr__(self) -> str:
        return f"<VisitaDireccionModel(id={self.id}, direccion_id={self.direccion_id}, resultado={self.resultado.value})>"
