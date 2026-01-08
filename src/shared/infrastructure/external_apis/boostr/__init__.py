"""
Boostr API Client.

Cliente para integración con la API de Boostr Chile.
https://docs.boostr.cl/reference

Servicios disponibles:
- Consulta de patentes (información de vehículos)
- Rutificador Plus (nombre, vehículos, propiedades, etc.)
- Multas de tránsito
- Revisión técnica
- SOAP
"""

from .client import BoostrClient, get_boostr_client, reset_boostr_client
from .schemas import (
    VehicleInfo,
    VehicleExtendedInfo,
    PersonInfo,
    PersonVehicle,
    TrafficFine,
    TechnicalReview,
    SOAPInfo,
    BoostrResponse,
)
from .exceptions import (
    BoostrAPIError,
    BoostrAuthenticationError,
    BoostrRateLimitError,
    BoostrNotFoundError,
    BoostrValidationError,
)

__all__ = [
    "BoostrClient",
    "get_boostr_client",
    "reset_boostr_client",
    "VehicleInfo",
    "VehicleExtendedInfo",
    "PersonInfo",
    "PersonVehicle",
    "TrafficFine",
    "TechnicalReview",
    "SOAPInfo",
    "BoostrResponse",
    "BoostrAPIError",
    "BoostrAuthenticationError",
    "BoostrRateLimitError",
    "BoostrNotFoundError",
    "BoostrValidationError",
]
