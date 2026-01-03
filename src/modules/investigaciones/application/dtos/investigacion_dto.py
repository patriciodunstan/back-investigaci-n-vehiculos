"""
DTOs para el modulo Investigaciones.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from src.shared.domain.enums import TipoActividadEnum, FuenteAvistamientoEnum


@dataclass(frozen=True)
class CreateActividadDTO:
    """DTO para crear actividad."""

    oficio_id: int
    tipo_actividad: TipoActividadEnum
    descripcion: str
    investigador_id: Optional[int] = None
    resultado: Optional[str] = None
    api_externa: Optional[str] = None
    datos_json: Optional[str] = None


@dataclass(frozen=True)
class CreateAvistamientoDTO:
    """DTO para crear avistamiento."""

    oficio_id: int
    fuente: FuenteAvistamientoEnum
    ubicacion: str
    fecha_hora: Optional[datetime] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    notas: Optional[str] = None
    api_response_id: Optional[str] = None
    datos_json: Optional[str] = None


@dataclass
class ActividadResponseDTO:
    """DTO de respuesta de actividad."""

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


@dataclass
class AvistamientoResponseDTO:
    """DTO de respuesta de avistamiento."""

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


@dataclass
class TimelineItemDTO:
    """DTO para item del timeline."""

    tipo: str  # "actividad" o "avistamiento"
    id: int
    fecha: datetime
    descripcion: str
    detalle: Optional[str] = None
    fuente: Optional[str] = None
    investigador_id: Optional[int] = None
