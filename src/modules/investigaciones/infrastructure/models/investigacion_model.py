"""
Modelo SQLAlchemy para Investigacion.

Representa una actividad en el timeline de investigación.

Principios aplicados:
- SRP: Solo define la estructura de la tabla investigaciones
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import TipoActividadEnum


class InvestigacionModel(Base):
    """
    Modelo de base de datos para actividades de investigación (timeline).

    Cada registro representa una acción realizada durante la investigación:
    - Consulta a API externa
    - Nota del investigador
    - Llamada telefónica
    - Visita en terreno

    Attributes:
        oficio_id: FK al oficio
        investigador_id: FK al usuario que realizó la actividad
        tipo_actividad: Tipo de actividad
        descripcion: Descripción de la actividad
        resultado: Resultado obtenido (opcional)
        api_externa: Nombre de API si aplica
        datos_json: Datos adicionales en JSON
        fecha_actividad: Fecha y hora de la actividad

    Relationships:
        oficio: Oficio al que pertenece
        investigador: Usuario que realizó la actividad
    """

    __tablename__ = "investigaciones"

    # Relaciones
    oficio_id = Column(
        Integer,
        ForeignKey("oficios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del oficio",
    )
    investigador_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del investigador que realizó la actividad",
    )

    # Datos de la actividad
    tipo_actividad = Column(
        Enum(TipoActividadEnum, name="tipo_actividad_enum", create_type=True),
        nullable=False,
        comment="Tipo de actividad",
    )
    descripcion = Column(Text, nullable=False, comment="Descripción de la actividad")
    resultado = Column(Text, nullable=True, comment="Resultado obtenido")

    # Para consultas a APIs
    api_externa = Column(
        String(100), nullable=True, comment="Nombre de la API externa si aplica"
    )
    datos_json = Column(
        Text, nullable=True, comment="Datos adicionales en formato JSON"
    )

    # Fecha de la actividad
    fecha_actividad = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Fecha y hora de la actividad",
    )

    # Relaciones
    oficio = relationship(
        "OficioModel", back_populates="investigaciones", lazy="joined"
    )
    investigador = relationship(
        "UsuarioModel", back_populates="investigaciones", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<InvestigacionModel(id={self.id}, tipo='{self.tipo_actividad.value}', fecha={self.fecha_actividad})>"
