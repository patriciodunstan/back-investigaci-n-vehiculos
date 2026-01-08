"""
DTOs para el modulo Oficios.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, date

from src.shared.domain.enums import (
    EstadoOficioEnum,
    PrioridadEnum,
    TipoPropietarioEnum,
    TipoDireccionEnum,
    ResultadoVerificacionEnum,
)


@dataclass(frozen=True)
class VehiculoDTO:
    """DTO para datos de vehiculo."""

    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    color: Optional[str] = None
    vin: Optional[str] = None


@dataclass(frozen=True)
class PropietarioDTO:
    """DTO para datos de propietario."""

    rut: str
    nombre_completo: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    tipo: TipoPropietarioEnum = TipoPropietarioEnum.PRINCIPAL
    direccion_principal: Optional[str] = None
    notas: Optional[str] = None


@dataclass(frozen=True)
class DireccionDTO:
    """DTO para datos de direccion."""

    direccion: str
    comuna: Optional[str] = None
    region: Optional[str] = None
    tipo: TipoDireccionEnum = TipoDireccionEnum.DOMICILIO
    notas: Optional[str] = None


@dataclass(frozen=True)
class CreateOficioDTO:
    """DTO para crear un oficio."""

    numero_oficio: str
    buffet_id: int
    vehiculo: VehiculoDTO
    prioridad: PrioridadEnum = PrioridadEnum.MEDIA
    fecha_limite: Optional[date] = None
    notas_generales: Optional[str] = None
    propietarios: Optional[List[PropietarioDTO]] = None
    direcciones: Optional[List[DireccionDTO]] = None


@dataclass(frozen=True)
class UpdateOficioDTO:
    """DTO para actualizar un oficio."""

    prioridad: Optional[PrioridadEnum] = None
    fecha_limite: Optional[date] = None
    notas_generales: Optional[str] = None


@dataclass(frozen=True)
class AsignarInvestigadorDTO:
    """DTO para asignar investigador."""

    investigador_id: int


@dataclass(frozen=True)
class CambiarEstadoDTO:
    """DTO para cambiar estado."""

    estado: EstadoOficioEnum


@dataclass
class VehiculoResponseDTO:
    """DTO de respuesta para vehiculo."""

    id: int
    patente: str
    marca: Optional[str]
    modelo: Optional[str]
    año: Optional[int]
    color: Optional[str]
    vin: Optional[str]


@dataclass
class PropietarioResponseDTO:
    """DTO de respuesta para propietario."""

    id: int
    rut: str
    nombre_completo: str
    email: Optional[str]
    telefono: Optional[str]
    tipo: str
    direccion_principal: Optional[str]
    notas: Optional[str]


@dataclass
class DireccionResponseDTO:
    """DTO de respuesta para direccion."""

    id: int
    direccion: str
    comuna: Optional[str]
    region: Optional[str]
    tipo: str
    verificada: bool
    resultado_verificacion: str
    fecha_verificacion: Optional[datetime]
    verificada_por_id: Optional[int]
    verificada_por_nombre: Optional[str]
    cantidad_visitas: int
    notas: Optional[str]


@dataclass
class VisitaDireccionDTO:
    """DTO para registrar una visita a dirección."""

    resultado: ResultadoVerificacionEnum
    notas: Optional[str] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None


@dataclass
class VisitaDireccionResponseDTO:
    """DTO de respuesta para una visita."""

    id: int
    direccion_id: int
    investigador_id: Optional[int]
    investigador_nombre: Optional[str]
    fecha_visita: datetime
    resultado: str
    notas: Optional[str]
    latitud: Optional[str]
    longitud: Optional[str]


@dataclass
class OficioResponseDTO:
    """DTO de respuesta para oficio."""

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
    vehiculo: Optional[VehiculoResponseDTO]
    propietarios: List[PropietarioResponseDTO]
    direcciones: List[DireccionResponseDTO]
    created_at: datetime
    updated_at: datetime
