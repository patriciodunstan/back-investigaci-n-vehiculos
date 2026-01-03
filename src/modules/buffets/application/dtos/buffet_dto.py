"""
DTOs para el modulo Buffets.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class CreateBuffetDTO:
    """DTO para crear un buffet."""

    nombre: str
    rut: str
    email_principal: str
    telefono: Optional[str] = None
    contacto_nombre: Optional[str] = None


@dataclass(frozen=True)
class UpdateBuffetDTO:
    """DTO para actualizar un buffet."""

    nombre: Optional[str] = None
    email_principal: Optional[str] = None
    telefono: Optional[str] = None
    contacto_nombre: Optional[str] = None


@dataclass
class BuffetResponseDTO:
    """DTO para respuesta con datos del buffet."""

    id: int
    nombre: str
    rut: str
    email_principal: str
    telefono: Optional[str]
    contacto_nombre: Optional[str]
    token_tablero: str
    activo: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, buffet) -> "BuffetResponseDTO":
        """Crea un DTO desde una entidad Buffet."""
        return cls(
            id=buffet.id,
            nombre=buffet.nombre,
            rut=buffet.rut_str if hasattr(buffet, "rut_str") else str(buffet.rut),
            email_principal=(
                buffet.email_str if hasattr(buffet, "email_str") else str(buffet.email_principal)
            ),
            telefono=buffet.telefono,
            contacto_nombre=buffet.contacto_nombre,
            token_tablero=buffet.token_tablero,
            activo=buffet.activo,
            created_at=buffet.created_at,
            updated_at=buffet.updated_at,
        )

    @classmethod
    def from_model(cls, model) -> "BuffetResponseDTO":
        """Crea un DTO desde un modelo SQLAlchemy."""
        return cls(
            id=model.id,
            nombre=model.nombre,
            rut=model.rut,
            email_principal=model.email_principal,
            telefono=model.telefono,
            contacto_nombre=model.contacto_nombre,
            token_tablero=model.token_tablero,
            activo=model.activo,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
