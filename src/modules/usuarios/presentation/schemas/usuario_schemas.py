"""
Schemas Pydantic para la API de usuarios.

Define los modelos de request/response para los endpoints.

Principios aplicados:
- Validacion automatica con Pydantic
- Documentacion OpenAPI automatica
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

from src.shared.domain.enums import RolEnum


class RegisterRequest(BaseModel):
    """Schema para registro de usuario."""

    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Contrasena (minimo 6 caracteres)",
    )
    nombre: str = Field(..., min_length=2, max_length=255, description="Nombre completo")
    rol: RolEnum = Field(default=RolEnum.CLIENTE, description="Rol del usuario")
    buffet_id: Optional[int] = Field(default=None, description="ID del buffet (solo para clientes)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "password123",
                "nombre": "Juan Perez",
                "rol": "cliente",
                "buffet_id": 1,
            }
        }
    )


class LoginRequest(BaseModel):
    """Schema para login de usuario."""

    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contrasena")

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "admin@test.com", "password": "admin123"}}
    )


class TokenResponse(BaseModel):
    """Schema para respuesta de token."""

    access_token: str = Field(..., description="Token JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta expiracion")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    )


class UserResponse(BaseModel):
    """Schema para respuesta con datos de usuario."""

    id: int = Field(..., description="ID del usuario")
    email: str = Field(..., description="Email del usuario")
    nombre: str = Field(..., description="Nombre completo")
    rol: str = Field(..., description="Rol del usuario")
    buffet_id: Optional[int] = Field(None, description="ID del buffet")
    activo: bool = Field(..., description="Si esta activo")
    avatar_url: Optional[str] = Field(None, description="URL del avatar")
    created_at: datetime = Field(..., description="Fecha de creacion")
    updated_at: datetime = Field(..., description="Fecha de actualizacion")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "admin@test.com",
                "nombre": "Admin Sistema",
                "rol": "admin",
                "buffet_id": None,
                "activo": True,
                "avatar_url": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        },
    )


class UpdateProfileRequest(BaseModel):
    """Schema para actualizar perfil."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=255, description="Nombre completo")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL del avatar")


class ChangePasswordRequest(BaseModel):
    """Schema para cambiar contrasena."""

    current_password: str = Field(..., description="Contrasena actual")
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Nueva contrasena (minimo 6 caracteres)",
    )


class MessageResponse(BaseModel):
    """Schema para respuestas simples con mensaje."""

    message: str = Field(..., description="Mensaje de respuesta")
    success: bool = Field(default=True, description="Si fue exitoso")


class UserListResponse(BaseModel):
    """Schema para lista de usuarios."""

    items: list[UserResponse] = Field(..., description="Lista de usuarios")
    total: int = Field(..., description="Total de usuarios")
    skip: int = Field(..., description="Registros saltados")
    limit: int = Field(..., description="Limite de registros")
