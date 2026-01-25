"""
Modelo SQLAlchemy para Propietario.

Representa un propietario o relacionado con el vehículo (N por oficio).

Principios aplicados:
- SRP: Solo define la estructura de la tabla propietarios
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import TipoPropietarioEnum


class PropietarioModel(Base):
    """
    Modelo de base de datos para propietarios.

    Un oficio puede tener múltiples propietarios:
    - Propietario principal
    - Codeudor
    - Aval
    - Usuario (familiar que usa el vehículo)

    Attributes:
        oficio_id: FK al oficio
        rut: RUT del propietario
        nombre_completo: Nombre completo
        email: Email de contacto (opcional)
        telefono: Teléfono de contacto (opcional)
        tipo: Tipo de propietario
        direccion_principal: Dirección principal conocida
        notas: Notas adicionales

    Relationships:
        oficio: Oficio al que pertenece

    Business Rules:
        - Un mismo RUT puede agregarse múltiples veces al mismo oficio (duplicados permitidos)
    """

    __tablename__ = "propietarios"

    # Relación con Oficio
    oficio_id = Column(
        Integer,
        ForeignKey("oficios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del oficio",
    )

    # Datos del propietario
    rut = Column(String(12), nullable=False, index=True, comment="RUT del propietario")
    nombre_completo = Column(String(255), nullable=False, comment="Nombre completo")
    email = Column(String(255), nullable=True, comment="Email de contacto")
    telefono = Column(String(20), nullable=True, comment="Teléfono de contacto")
    tipo = Column(
        Enum(TipoPropietarioEnum, name="tipo_propietario_enum", create_type=True),
        nullable=False,
        default=TipoPropietarioEnum.PRINCIPAL,
        comment="Tipo de propietario",
    )
    direccion_principal = Column(
        String(500), nullable=True, comment="Dirección principal conocida"
    )
    notas = Column(Text, nullable=True, comment="Notas adicionales")

    # Relación
    oficio = relationship("OficioModel", back_populates="propietarios", lazy="joined")

    def __repr__(self) -> str:
        return f"<PropietarioModel(id={self.id}, rut='{self.rut}', tipo='{self.tipo.value}')>"
