"""
Modelo SQLAlchemy para Vehiculo.

Representa el vehículo objeto de investigación (relación 1:1 con Oficio).

Principios aplicados:
- SRP: Solo define la estructura de la tabla vehiculos
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.shared.infrastructure.database.base import Base


class VehiculoModel(Base):
    """
    Modelo de base de datos para vehículos.

    Attributes:
        oficio_id: FK al oficio (relación 1:N)
        patente: Patente del vehículo (ej: "ABCD12")
        marca: Marca del vehículo (ej: "Toyota")
        modelo: Modelo del vehículo (ej: "Corolla")
        año: Año del vehículo
        color: Color del vehículo
        vin: Número de identificación vehicular (VIN)

    Relationships:
        oficio: Oficio al que pertenece este vehículo

    Business Rules:
        - Un mismo vehículo puede agregarse múltiples veces al mismo oficio (duplicados permitidos)
    """

    __tablename__ = "vehiculos"

    # Relación 1:N con Oficio (un oficio puede tener múltiples vehículos)
    oficio_id = Column(
        Integer,
        ForeignKey("oficios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del oficio (relación 1:N)",
    )

    # Datos del vehículo
    patente = Column(
        String(10), nullable=False, index=True, comment="Patente del vehículo"
    )
    marca = Column(String(100), nullable=True, comment="Marca del vehículo")
    modelo = Column(String(100), nullable=True, comment="Modelo del vehículo")
    año = Column(Integer, nullable=True, comment="Año del vehículo")
    color = Column(String(50), nullable=True, comment="Color del vehículo")
    vin = Column(
        String(17), nullable=True, comment="Número de identificación vehicular (VIN)"
    )

    # Relación
    oficio = relationship("OficioModel", back_populates="vehiculos", lazy="joined")

    def __repr__(self) -> str:
        return f"<VehiculoModel(id={self.id}, patente='{self.patente}', marca='{self.marca}')>"
