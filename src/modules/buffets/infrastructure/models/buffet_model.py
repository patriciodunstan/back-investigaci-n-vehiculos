"""
Modelo SQLAlchemy para Buffet.

Representa un estudio jurídico o empresa de cobranza cliente del sistema.

Principios aplicados:
- SRP: Solo define la estructura de la tabla buffets
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
import secrets

from src.shared.infrastructure.database.base import Base


class BuffetModel(Base):
    """
    Modelo de base de datos para buffets (estudios jurídicos).

    Attributes:
        nombre: Nombre del buffet (ej: "Buffet González y Asociados")
        rut: RUT único del buffet (ej: "76.123.456-7")
        email_principal: Email de contacto principal
        telefono: Teléfono de contacto
        contacto_nombre: Nombre de la persona de contacto
        token_tablero: Token único para acceso al dashboard público
        activo: Si el buffet está activo (soft delete)

    Relationships:
        usuarios: Usuarios asociados a este buffet (clientes)
        oficios: Oficios/casos de este buffet
    """

    __tablename__ = "buffets"

    # Campos principales
    nombre = Column(String(255), nullable=False, comment="Nombre del estudio jurídico")
    rut = Column(
        String(12),
        unique=True,
        nullable=False,
        index=True,
        comment="RUT único del buffet",
    )
    email_principal = Column(
        String(255), nullable=False, comment="Email de contacto principal"
    )
    telefono = Column(String(20), nullable=True, comment="Teléfono de contacto")
    contacto_nombre = Column(
        String(255), nullable=True, comment="Nombre de la persona de contacto"
    )

    # Token para dashboard público
    token_tablero = Column(
        String(64),
        unique=True,
        nullable=False,
        default=lambda: secrets.token_urlsafe(32),
        comment="Token para acceso al tablero público",
    )

    # Soft delete
    activo = Column(
        Boolean, default=True, nullable=False, comment="Si el buffet está activo"
    )

    # Relaciones (se definirán cuando creemos los otros modelos)
    usuarios = relationship("UsuarioModel", back_populates="buffet", lazy="dynamic")
    oficios = relationship("OficioModel", back_populates="buffet", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<BuffetModel(id={self.id}, nombre='{self.nombre}', rut='{self.rut}')>"
