"""DTOs del modulo Oficios"""

from .oficio_dto import (
    VehiculoDTO,
    PropietarioDTO,
    DireccionDTO,
    CreateOficioDTO,
    UpdateOficioDTO,
    AsignarInvestigadorDTO,
    CambiarEstadoDTO,
    VehiculoResponseDTO,
    PropietarioResponseDTO,
    DireccionResponseDTO,
    OficioResponseDTO,
    VisitaDireccionDTO,
    VisitaDireccionResponseDTO,
)
from .documento_extraido_dto import (
    OficioExtraidoDTO,
    CAVExtraidoDTO,
    ParDocumentoDTO,
)

__all__ = [
    "VehiculoDTO",
    "PropietarioDTO",
    "DireccionDTO",
    "CreateOficioDTO",
    "UpdateOficioDTO",
    "AsignarInvestigadorDTO",
    "CambiarEstadoDTO",
    "VehiculoResponseDTO",
    "PropietarioResponseDTO",
    "DireccionResponseDTO",
    "OficioResponseDTO",
    "VisitaDireccionDTO",
    "VisitaDireccionResponseDTO",
    "OficioExtraidoDTO",
    "CAVExtraidoDTO",
    "ParDocumentoDTO",
]
