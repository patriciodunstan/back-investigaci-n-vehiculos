"""
Boostr API Client (Rutificador).

Cliente para integración con la API de Boostr Chile.
https://docs.boostr.cl/reference

Endpoints disponibles:
- /rut/vehicles/{rut}.json - Vehículos por RUT
- /rut/properties/{rut}.json - Propiedades por RUT
- /rut/deceased/{rut}.json - Estado de defunción
"""

from .client import BoostrClient, get_boostr_client, reset_boostr_client
from .schemas import (
    PersonVehicle,
    PersonProperty,
    DeceasedInfo,
)
from .exceptions import (
    BoostrAPIError,
    BoostrAuthenticationError,
    BoostrRateLimitError,
    BoostrNotFoundError,
    BoostrValidationError,
)

__all__ = [
    # Client
    "BoostrClient",
    "get_boostr_client",
    "reset_boostr_client",
    # Schemas
    "PersonVehicle",
    "PersonProperty",
    "DeceasedInfo",
    # Exceptions
    "BoostrAPIError",
    "BoostrAuthenticationError",
    "BoostrRateLimitError",
    "BoostrNotFoundError",
    "BoostrValidationError",
]
