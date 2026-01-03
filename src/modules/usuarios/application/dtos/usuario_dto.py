"""
DTOs (Data Transfer Objects) para el modulo Usuarios.

Define las estructuras de datos para comunicacion entre capas.

Principios aplicados:
- SRP: Solo define estructuras de datos
- Inmutabilidad: Dataclasses con frozen=True donde aplica
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from src.shared.domain.enums import RolEnum


@dataclass(frozen=True)
class RegisterUserDTO:
    """DTO para registrar un nuevo usuario."""

    email: str
    password: str
    nombre: str
    rol: RolEnum = RolEnum.CLIENTE
    buffet_id: Optional[int] = None


@dataclass(frozen=True)
class LoginDTO:
    """DTO para login de usuario."""

    email: str
    password: str


@dataclass(frozen=True)
class TokenResponseDTO:
    """DTO para respuesta de login con token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # segundos


@dataclass
class UserResponseDTO:
    """DTO para respuesta con datos del usuario."""

    id: int
    email: str
    nombre: str
    rol: str
    buffet_id: Optional[int]
    activo: bool
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, usuario) -> "UserResponseDTO":
        """Crea un DTO desde una entidad Usuario."""
        return cls(
            id=usuario.id,
            email=(
                usuario.email_str
                if hasattr(usuario, "email_str")
                else str(usuario.email)
            ),
            nombre=usuario.nombre,
            rol=(
                usuario.rol.value if hasattr(usuario.rol, "value") else str(usuario.rol)
            ),
            buffet_id=usuario.buffet_id,
            activo=usuario.activo,
            avatar_url=usuario.avatar_url,
            created_at=usuario.created_at,
            updated_at=usuario.updated_at,
        )

    @classmethod
    def from_model(cls, model) -> "UserResponseDTO":
        """Crea un DTO desde un modelo SQLAlchemy."""
        return cls(
            id=model.id,
            email=model.email,
            nombre=model.nombre,
            rol=model.rol.value if hasattr(model.rol, "value") else str(model.rol),
            buffet_id=model.buffet_id,
            activo=model.activo,
            avatar_url=model.avatar_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@dataclass(frozen=True)
class UpdateUserDTO:
    """DTO para actualizar datos del usuario."""

    nombre: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass(frozen=True)
class ChangePasswordDTO:
    """DTO para cambiar contrasena."""

    current_password: str
    new_password: str
