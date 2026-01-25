"""
Router para consultas a la API de Boostr (Rutificador).

Endpoints para consultar información de personas por RUT:
- Vehículos registrados a su nombre
- Propiedades registradas a su nombre
- Estado de defunción
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.shared.infrastructure.external_apis.boostr import (
    BoostrClient,
    get_boostr_client,
    BoostrAPIError,
    BoostrAuthenticationError,
    BoostrRateLimitError,
    BoostrValidationError,
)
from src.modules.usuarios.presentation.routers import get_current_user
from src.modules.usuarios.presentation.schemas import UserResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/boostr", tags=["Boostr API"])


# =============================================================================
# SCHEMAS DE RESPUESTA
# =============================================================================


class VehiculoResponse(BaseModel):
    """Vehículo registrado a nombre de una persona."""

    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = Field(None, alias="anio")
    tipo: Optional[str] = None

    class Config:
        populate_by_name = True


class PropiedadResponse(BaseModel):
    """Propiedad registrada a nombre de una persona."""

    rol: Optional[str] = None
    comuna: Optional[str] = None
    direccion: Optional[str] = None
    destino: Optional[str] = None
    avaluo: Optional[float] = None


class DefuncionResponse(BaseModel):
    """Estado de defunción de una persona."""

    rut: str
    fallecido: bool = False
    fecha_defuncion: Optional[str] = None


class BoostrErrorResponse(BaseModel):
    """Respuesta de error de Boostr."""

    detail: str
    code: Optional[str] = None


# =============================================================================
# DEPENDENCY
# =============================================================================


def get_boostr() -> BoostrClient:
    """Obtiene el cliente de Boostr."""
    return get_boostr_client()


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.get(
    "/rut/{rut}/vehiculos",
    response_model=list[VehiculoResponse],
    summary="Consultar vehículos por RUT",
    description="Obtiene todos los vehículos registrados a nombre de un RUT.",
    responses={
        400: {"model": BoostrErrorResponse, "description": "RUT inválido"},
        429: {"model": BoostrErrorResponse, "description": "Rate limit excedido"},
        502: {"model": BoostrErrorResponse, "description": "Error en servicio externo"},
    },
)
async def get_vehiculos_por_rut(
    rut: str,
    client: BoostrClient = Depends(get_boostr),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Consulta los vehículos registrados a nombre de un RUT.

    **Parámetros:**
    - `rut`: RUT de la persona o empresa (ej: 12.345.678-9)

    **Retorna:**
    - Lista de vehículos con patente, marca, modelo, año y tipo

    **Consume 1 crédito de Boostr.**
    """
    try:
        vehicles = await client.get_person_vehicles(rut)

        return [
            VehiculoResponse(
                patente=v.patente,
                marca=v.marca,
                modelo=v.modelo,
                año=v.año,
                tipo=v.tipo,
            )
            for v in vehicles
        ]

    except BoostrValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RUT inválido: {rut}",
        )
    except BoostrRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit excedido. Intente en 1 minuto.",
        )
    except BoostrAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación con Boostr API",
        )
    except BoostrAPIError as e:
        logger.error(f"Error consultando vehículos de {rut}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )


@router.get(
    "/rut/{rut}/propiedades",
    response_model=list[PropiedadResponse],
    summary="Consultar propiedades por RUT",
    description="Obtiene todas las propiedades (bienes raíces) registradas a nombre de un RUT.",
    responses={
        400: {"model": BoostrErrorResponse, "description": "RUT inválido"},
        429: {"model": BoostrErrorResponse, "description": "Rate limit excedido"},
        502: {"model": BoostrErrorResponse, "description": "Error en servicio externo"},
    },
)
async def get_propiedades_por_rut(
    rut: str,
    client: BoostrClient = Depends(get_boostr),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Consulta las propiedades registradas a nombre de un RUT.

    **Parámetros:**
    - `rut`: RUT de la persona o empresa (ej: 12.345.678-9)

    **Retorna:**
    - Lista de propiedades con rol, comuna, dirección, destino y avalúo

    **Consume 1 crédito de Boostr.**
    """
    try:
        properties = await client.get_person_properties(rut)

        return [
            PropiedadResponse(
                rol=p.rol,
                comuna=p.comuna,
                direccion=p.direccion,
                destino=p.destino,
                avaluo=p.avaluo,
            )
            for p in properties
        ]

    except BoostrValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RUT inválido: {rut}",
        )
    except BoostrRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit excedido. Intente en 1 minuto.",
        )
    except BoostrAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación con Boostr API",
        )
    except BoostrAPIError as e:
        logger.error(f"Error consultando propiedades de {rut}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )


@router.get(
    "/rut/{rut}/defuncion",
    response_model=DefuncionResponse,
    summary="Verificar defunción por RUT",
    description="Verifica si una persona ha fallecido según registros oficiales.",
    responses={
        400: {"model": BoostrErrorResponse, "description": "RUT inválido"},
        429: {"model": BoostrErrorResponse, "description": "Rate limit excedido"},
        502: {"model": BoostrErrorResponse, "description": "Error en servicio externo"},
    },
)
async def check_defuncion_por_rut(
    rut: str,
    client: BoostrClient = Depends(get_boostr),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Verifica si una persona ha fallecido.

    **Parámetros:**
    - `rut`: RUT de la persona (ej: 12.345.678-9)

    **Retorna:**
    - Estado de defunción (fallecido: true/false)
    - Fecha de defunción si aplica

    **Consume 1 crédito de Boostr.**
    """
    try:
        deceased_info = await client.check_deceased(rut)

        return DefuncionResponse(
            rut=rut,
            fallecido=deceased_info.fallecido,
            fecha_defuncion=deceased_info.fecha_defuncion,
        )

    except BoostrValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RUT inválido: {rut}",
        )
    except BoostrRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit excedido. Intente en 1 minuto.",
        )
    except BoostrAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación con Boostr API",
        )
    except BoostrAPIError as e:
        logger.error(f"Error verificando defunción de {rut}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )
