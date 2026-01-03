"""Excepciones del modulo Oficios"""

from .oficio_exceptions import (
    OficioNotFoundException,
    NumeroOficioAlreadyExistsException,
    OficioYaFinalizadoException,
    VehiculoNotFoundException,
    PropietarioNotFoundException,
    DireccionNotFoundException,
)

__all__ = [
    "OficioNotFoundException",
    "NumeroOficioAlreadyExistsException",
    "OficioYaFinalizadoException",
    "VehiculoNotFoundException",
    "PropietarioNotFoundException",
    "DireccionNotFoundException",
]
