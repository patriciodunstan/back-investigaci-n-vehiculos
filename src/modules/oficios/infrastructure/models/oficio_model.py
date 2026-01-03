"""
Modelo SQLAlchemy para Oficio.

Representa un caso de investigación vehicular.

Principios aplicados:
- SRP: Solo define la estructura de la tabla oficios
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Date, Text
from sqlalchemy.orm import relationship
from datetime import date

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import EstadoOficioEnum, PrioridadEnum


class OficioModel(Base):
    """
    Modelo de base de datos para oficios (casos de investigación).

    Attributes:
        numero_oficio: Número único del oficio (ej: "OF-2024-001")
        buffet_id: FK al buffet que solicitó la investigación
        investigador_id: FK al investigador asignado (opcional)
        estado: Estado actual del oficio
        prioridad: Nivel de prioridad
        fecha_ingreso: Fecha de creación del oficio
        fecha_limite: Fecha límite para completar (opcional)
        notas_generales: Notas o comentarios generales

    Relationships:
        buffet: Buffet que solicitó la investigación
        investigador: Usuario investigador asignado
        vehiculo: Vehículo a investigar (1:1)
        propietarios: Propietarios del vehículo
        direcciones: Direcciones a verificar
        investigaciones: Timeline de actividades
        avistamientos: Resultados de APIs
        adjuntos: Fotos y documentos
        notificaciones: Emails enviados
    """

    __tablename__ = "oficios"

    # Identificador único
    numero_oficio = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Número único del oficio (ej: OF-2024-001)",
    )

    # Relaciones principales
    buffet_id = Column(
        Integer,
        ForeignKey("buffets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del buffet que solicitó la investigación",
    )
    investigador_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del investigador asignado",
    )

    # Estado y prioridad
    estado = Column(
        Enum(EstadoOficioEnum, name="estado_oficio_enum", create_type=True),
        nullable=False,
        default=EstadoOficioEnum.PENDIENTE,
        index=True,
        comment="Estado actual del oficio",
    )
    prioridad = Column(
        Enum(PrioridadEnum, name="prioridad_enum", create_type=True),
        nullable=False,
        default=PrioridadEnum.MEDIA,
        comment="Nivel de prioridad",
    )

    # Fechas
    fecha_ingreso = Column(
        Date, nullable=False, default=date.today, comment="Fecha de ingreso del oficio"
    )
    fecha_limite = Column(Date, nullable=True, comment="Fecha límite para completar")

    # Notas
    notas_generales = Column(
        Text, nullable=True, comment="Notas o comentarios generales"
    )

    # Relaciones
    buffet = relationship("BuffetModel", back_populates="oficios", lazy="joined")
    investigador = relationship(
        "UsuarioModel",
        back_populates="oficios_asignados",
        foreign_keys=[investigador_id],
        lazy="joined",
    )
    vehiculo = relationship(
        "VehiculoModel",
        back_populates="oficio",
        uselist=False,  # Relación 1:1
        lazy="joined",
        cascade="all, delete-orphan",
    )
    propietarios = relationship(
        "PropietarioModel",
        back_populates="oficio",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    direcciones = relationship(
        "DireccionModel",
        back_populates="oficio",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    investigaciones = relationship(
        "InvestigacionModel",
        back_populates="oficio",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    avistamientos = relationship(
        "AvistamientoModel",
        back_populates="oficio",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    adjuntos = relationship(
        "AdjuntoModel",
        back_populates="oficio",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    notificaciones = relationship(
        "NotificacionModel",
        back_populates="oficio",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<OficioModel(id={self.id}, numero='{self.numero_oficio}', estado='{self.estado.value}')>"
