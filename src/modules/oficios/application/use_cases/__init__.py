"""Use Cases del modulo Oficios"""

from .create_oficio import CreateOficioUseCase
from .get_oficio import GetOficioUseCase
from .update_oficio import (
    UpdateOficioUseCase,
    AsignarInvestigadorUseCase,
    CambiarEstadoUseCase,
    AgregarPropietarioUseCase,
    AgregarDireccionUseCase,
)

__all__ = [
    "CreateOficioUseCase",
    "GetOficioUseCase",
    "UpdateOficioUseCase",
    "AsignarInvestigadorUseCase",
    "CambiarEstadoUseCase",
    "AgregarPropietarioUseCase",
    "AgregarDireccionUseCase",
]
