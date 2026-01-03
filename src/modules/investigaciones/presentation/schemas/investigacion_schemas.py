"""
Schemas Pydantic para la API de investigaciones.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from src.shared.domain.enums import TipoActividadEnum, FuenteAvistamientoEnum


class CreateActividadRequest(BaseModel):
    """Schema para crear actividad."""

    tipo_actividad: TipoActividadEnum = Field(default=TipoActividadEnum.NOTA)
    descripcion: str = Field(..., min_length=5, max_length=2000)
    resultado: Optional[str] = Field(None, max_length=2000)
    api_externa: Optional[str] = Field(None, max_length=100)
    datos_json: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tipo_actividad": "nota",
                "descripcion": "Visita a direccion registrada",
                "resultado": "No se encontro el vehiculo",
            }
        }
    )


class CreateAvistamientoRequest(BaseModel):
    """Schema para crear avistamiento."""

    fuente: FuenteAvistamientoEnum = Field(default=FuenteAvistamientoEnum.TERRENO)
    ubicacion: str = Field(..., min_length=5, max_length=500)
    fecha_hora: Optional[datetime] = None
    latitud: Optional[float] = Field(None, ge=-90, le=90)
    longitud: Optional[float] = Field(None, ge=-180, le=180)
    notas: Optional[str] = Field(None, max_length=1000)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fuente": "terreno",
                "ubicacion": "Av. Providencia 1234, Providencia",
                "latitud": -33.4269,
                "longitud": -70.6150,
                "notas": "Vehiculo estacionado frente al edificio",
            }
        }
    )


class ActividadResponse(BaseModel):
    """Schema de respuesta de actividad."""

    id: int
    oficio_id: int
    investigador_id: Optional[int]
    tipo_actividad: str
    descripcion: str
    resultado: Optional[str]
    api_externa: Optional[str]
    datos_json: Optional[str]
    fecha_actividad: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AvistamientoResponse(BaseModel):
    """Schema de respuesta de avistamiento."""

    id: int
    oficio_id: int
    fuente: str
    fecha_hora: datetime
    ubicacion: str
    latitud: Optional[float]
    longitud: Optional[float]
    api_response_id: Optional[str]
    datos_json: Optional[str]
    notas: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimelineItemResponse(BaseModel):
    """Schema de item del timeline."""

    tipo: str
    id: int
    fecha: datetime
    descripcion: str
    detalle: Optional[str]
    fuente: Optional[str]
    investigador_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class TimelineResponse(BaseModel):
    """Schema de respuesta del timeline."""

    oficio_id: int
    items: List[TimelineItemResponse]
    total: int
