"""
Schemas Pydantic para la API de buffets.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CreateBuffetRequest(BaseModel):
    """Schema para crear buffet."""

    nombre: str = Field(..., min_length=2, max_length=255, description="Nombre del buffet")
    rut: str = Field(..., description="RUT del buffet (ej: 12345678-9)")
    email_principal: EmailStr = Field(..., description="Email de contacto")
    telefono: Optional[str] = Field(None, max_length=20, description="Telefono")
    contacto_nombre: Optional[str] = Field(None, max_length=255, description="Nombre contacto")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Estudio Juridico ABC",
                "rut": "76123456-7",
                "email_principal": "contacto@abc.cl",
                "telefono": "+56912345678",
                "contacto_nombre": "Juan Perez",
            }
        }
    )


class UpdateBuffetRequest(BaseModel):
    """Schema para actualizar buffet."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    email_principal: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    contacto_nombre: Optional[str] = Field(None, max_length=255)


class BuffetResponse(BaseModel):
    """Schema para respuesta de buffet."""

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

    model_config = ConfigDict(from_attributes=True)


class BuffetListResponse(BaseModel):
    """Schema para lista de buffets."""

    items: list[BuffetResponse]
    total: int
    skip: int
    limit: int
