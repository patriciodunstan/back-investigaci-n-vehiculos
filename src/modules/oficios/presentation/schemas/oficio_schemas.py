"""
Schemas Pydantic para la API de oficios.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date

from src.shared.domain.enums import (
    EstadoOficioEnum,
    PrioridadEnum,
    TipoPropietarioEnum,
    TipoDireccionEnum,
    ResultadoVerificacionEnum,
)


class VehiculoRequest(BaseModel):
    """Schema para datos de vehiculo."""

    patente: str = Field(..., min_length=6, max_length=10, description="Patente del vehiculo")
    marca: Optional[str] = Field(None, max_length=100)
    modelo: Optional[str] = Field(None, max_length=100)
    año: Optional[int] = Field(None, ge=1900, le=2100)
    color: Optional[str] = Field(None, max_length=50)
    vin: Optional[str] = Field(None, max_length=17)


class PropietarioRequest(BaseModel):
    """Schema para datos de propietario."""

    rut: str = Field(..., description="RUT del propietario")
    nombre_completo: str = Field(..., max_length=255)
    email: Optional[str] = None
    telefono: Optional[str] = Field(None, max_length=20)
    tipo: TipoPropietarioEnum = TipoPropietarioEnum.PRINCIPAL
    direccion_principal: Optional[str] = Field(None, max_length=500)
    notas: Optional[str] = None


class DireccionRequest(BaseModel):
    """Schema para datos de direccion."""

    direccion: str = Field(..., max_length=500)
    comuna: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    tipo: TipoDireccionEnum = TipoDireccionEnum.DOMICILIO
    notas: Optional[str] = None


class RegistrarVisitaRequest(BaseModel):
    """Schema para registrar una visita a una dirección."""

    resultado: ResultadoVerificacionEnum = Field(
        ..., 
        description="Resultado de la visita"
    )
    notas: Optional[str] = Field(
        None, 
        max_length=2000,
        description="Notas sobre la visita"
    )
    latitud: Optional[str] = Field(
        None, 
        max_length=20,
        description="Latitud GPS de la visita"
    )
    longitud: Optional[str] = Field(
        None, 
        max_length=20,
        description="Longitud GPS de la visita"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "resultado": "no_encontrado",
                "notas": "Se visitó a las 15:00, nadie respondió",
                "latitud": "-33.4489",
                "longitud": "-70.6693",
            }
        }
    )


class CreateOficioRequest(BaseModel):
    """Schema para crear oficio."""

    numero_oficio: str = Field(..., max_length=50, description="Numero del oficio")
    buffet_id: int = Field(..., description="ID del buffet solicitante")
    vehiculo: VehiculoRequest
    prioridad: PrioridadEnum = PrioridadEnum.MEDIA
    fecha_limite: Optional[date] = None
    notas_generales: Optional[str] = None
    propietarios: Optional[List[PropietarioRequest]] = None
    direcciones: Optional[List[DireccionRequest]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "numero_oficio": "OF-2024-001",
                "buffet_id": 1,
                "vehiculo": {
                    "patente": "ABCD12",
                    "marca": "Toyota",
                    "modelo": "Corolla",
                    "año": 2020,
                    "color": "Blanco",
                },
                "prioridad": "media",
                "propietarios": [
                    {
                        "rut": "12345678-9",
                        "nombre_completo": "Juan Perez",
                        "tipo": "principal",
                    }
                ],
            }
        }
    )


class UpdateOficioRequest(BaseModel):
    """Schema para actualizar oficio."""

    prioridad: Optional[PrioridadEnum] = None
    fecha_limite: Optional[date] = None
    notas_generales: Optional[str] = None


class AsignarInvestigadorRequest(BaseModel):
    """Schema para asignar investigador."""

    investigador_id: int


class CambiarEstadoRequest(BaseModel):
    """Schema para cambiar estado."""

    estado: EstadoOficioEnum


class VehiculoResponse(BaseModel):
    """Schema de respuesta para vehiculo."""

    id: int
    patente: str
    marca: Optional[str]
    modelo: Optional[str]
    año: Optional[int]
    color: Optional[str]
    vin: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class PropietarioResponse(BaseModel):
    """Schema de respuesta para propietario."""

    id: int
    rut: str
    nombre_completo: str
    email: Optional[str]
    telefono: Optional[str]
    tipo: str
    direccion_principal: Optional[str]
    notas: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class VisitaDireccionResponse(BaseModel):
    """Schema de respuesta para una visita a dirección."""

    id: int
    direccion_id: int
    investigador_id: Optional[int]
    investigador_nombre: Optional[str] = None
    fecha_visita: datetime
    resultado: str
    notas: Optional[str]
    latitud: Optional[str]
    longitud: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class DireccionResponse(BaseModel):
    """Schema de respuesta para direccion."""

    id: int
    direccion: str
    comuna: Optional[str]
    region: Optional[str]
    tipo: str
    verificada: bool
    resultado_verificacion: str = "pendiente"
    fecha_verificacion: Optional[datetime]
    verificada_por_id: Optional[int] = None
    verificada_por_nombre: Optional[str] = None
    cantidad_visitas: int = 0
    notas: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class OficioResponse(BaseModel):
    """Schema de respuesta para oficio."""

    id: int
    numero_oficio: str
    buffet_id: int
    buffet_nombre: Optional[str]
    investigador_id: Optional[int]
    investigador_nombre: Optional[str]
    estado: str
    prioridad: str
    fecha_ingreso: date
    fecha_limite: Optional[date]
    notas_generales: Optional[str]
    vehiculo: Optional[VehiculoResponse]
    propietarios: List[PropietarioResponse]
    direcciones: List[DireccionResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OficioListResponse(BaseModel):
    """Schema para lista de oficios."""

    items: List[OficioResponse]
    total: int
    skip: int
    limit: int
