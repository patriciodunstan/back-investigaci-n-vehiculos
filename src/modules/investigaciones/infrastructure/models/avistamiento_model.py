"""
Modelo SQLAlchemy para Avistamiento.

Representa un registro de avistamiento del vehículo (pórticos, multas, etc).

Principios aplicados:
- SRP: Solo define la estructura de la tabla avistamientos
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Text, Float
from sqlalchemy.orm import relationship

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import FuenteAvistamientoEnum


class AvistamientoModel(Base):
    """
    Modelo de base de datos para avistamientos.

    Registra cada vez que el vehículo fue detectado:
    - Pórticos de peaje (API Boostr)
    - Multas de tránsito
    - Avistamientos en terreno

    Attributes:
        oficio_id: FK al oficio
        fuente: Fuente del avistamiento
        fecha_hora: Fecha y hora del avistamiento
        ubicacion: Ubicación textual
        latitud: Coordenada de latitud (opcional)
        longitud: Coordenada de longitud (opcional)
        api_response_id: ID de respuesta de API (opcional)
        datos_json: Datos adicionales en JSON
        notas: Notas adicionales

    Relationships:
        oficio: Oficio al que pertenece
    """

    __tablename__ = "avistamientos"

    # Relación con Oficio
    oficio_id = Column(
        Integer,
        ForeignKey("oficios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del oficio",
    )

    # Fuente del avistamiento
    fuente = Column(
        Enum(FuenteAvistamientoEnum, name="fuente_avistamiento_enum", create_type=True),
        nullable=False,
        comment="Fuente del avistamiento",
    )

    # Datos del avistamiento
    fecha_hora = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Fecha y hora del avistamiento",
    )
    ubicacion = Column(
        String(500), nullable=False, comment="Ubicación textual del avistamiento"
    )

    # Coordenadas (opcionales)
    latitud = Column(Float, nullable=True, comment="Latitud del avistamiento")
    longitud = Column(Float, nullable=True, comment="Longitud del avistamiento")

    # Datos de API
    api_response_id = Column(
        String(100), nullable=True, comment="ID de la respuesta de la API externa"
    )
    datos_json = Column(
        Text, nullable=True, comment="Datos adicionales en formato JSON"
    )

    # Notas
    notas = Column(Text, nullable=True, comment="Notas adicionales")

    # Relación
    oficio = relationship("OficioModel", back_populates="avistamientos", lazy="joined")

    def __repr__(self) -> str:
        return f"<AvistamientoModel(id={self.id}, fuente='{self.fuente.value}', fecha={self.fecha_hora})>"
