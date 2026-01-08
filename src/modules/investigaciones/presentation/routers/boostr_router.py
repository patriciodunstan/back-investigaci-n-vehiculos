"""
Router para consultas a la API de Boostr.

Endpoints para consultar información de vehículos y personas
a través de la API de Boostr Chile.
"""

import json
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.shared.infrastructure.database import get_db
from src.shared.infrastructure.external_apis.boostr import (
    BoostrClient,
    get_boostr_client,
    BoostrAPIError,
    BoostrAuthenticationError,
    BoostrRateLimitError,
    BoostrNotFoundError,
    BoostrValidationError,
    VehicleExtendedInfo,
    PersonInfo,
    PersonVehicle,
    TrafficFine,
)
from src.modules.usuarios.presentation.routers import get_current_user
from src.modules.usuarios.presentation.schemas import UserResponse
from src.modules.investigaciones.infrastructure.repositories import (
    InvestigacionRepository,
)
from src.modules.investigaciones.application.dtos import CreateActividadDTO
from src.modules.investigaciones.application.use_cases import AddActividadUseCase
from src.shared.domain.enums import TipoActividadEnum


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/boostr", tags=["Boostr API"])


# =============================================================================
# SCHEMAS DE RESPUESTA
# =============================================================================

class VehicleInfoResponse(BaseModel):
    """Respuesta de información de vehículo."""
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    tipo: Optional[str] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    combustible: Optional[str] = None
    kilometraje: Optional[int] = None
    propietario_rut: Optional[str] = None
    propietario_nombre: Optional[str] = None


class PersonInfoResponse(BaseModel):
    """Respuesta de información de persona."""
    rut: str
    nombre: Optional[str] = None
    nombres: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    genero: Optional[str] = None
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    edad: Optional[int] = None
    fallecido: Optional[bool] = None


class PersonVehicleResponse(BaseModel):
    """Vehículo asociado a una persona."""
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    tipo: Optional[str] = None


class TrafficFineResponse(BaseModel):
    """Multa de tránsito."""
    juzgado: Optional[str] = None
    comuna: Optional[str] = None
    rol: Optional[str] = None
    año: Optional[int] = None
    fecha: Optional[str] = None
    estado: Optional[str] = None
    monto: Optional[float] = None


class InvestigacionVehiculoResponse(BaseModel):
    """Respuesta de investigación completa de vehículo."""
    vehiculo: Optional[VehicleInfoResponse] = None
    multas: List[TrafficFineResponse] = []
    creditos_usados: int = 0
    fecha_consulta: datetime


class InvestigacionPropietarioResponse(BaseModel):
    """Respuesta de investigación completa de propietario."""
    propietario: Optional[PersonInfoResponse] = None
    vehiculos: List[PersonVehicleResponse] = []
    creditos_usados: int = 0
    fecha_consulta: datetime


class BoostrErrorResponse(BaseModel):
    """Respuesta de error de Boostr."""
    detail: str
    code: Optional[str] = None
    status_code: int


# =============================================================================
# DEPENDENCIES
# =============================================================================

def get_boostr() -> BoostrClient:
    """Obtiene el cliente de Boostr."""
    return get_boostr_client()


def get_investigacion_repository(
    db: Session = Depends(get_db),
) -> InvestigacionRepository:
    """Dependency para obtener el repositorio."""
    return InvestigacionRepository(db)


# =============================================================================
# ENDPOINTS DE VEHÍCULOS
# =============================================================================

@router.get(
    "/vehiculo/{patente}",
    response_model=VehicleInfoResponse,
    summary="Consultar vehículo por patente",
    responses={
        404: {"model": BoostrErrorResponse, "description": "Vehículo no encontrado"},
        429: {"model": BoostrErrorResponse, "description": "Rate limit excedido"},
    },
)
async def get_vehicle_info(
    patente: str,
    client: BoostrClient = Depends(get_boostr),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Consulta información de un vehículo por su patente.
    
    Datos obtenidos:
    - Marca, modelo, año, tipo
    - Color, VIN (versión extendida)
    - Propietario (si está disponible)
    
    **Consume 1 crédito de Boostr.**
    """
    try:
        vehicle = await client.get_vehicle_info(patente)
        
        return VehicleInfoResponse(
            patente=vehicle.patente,
            marca=vehicle.marca,
            modelo=vehicle.modelo,
            año=vehicle.año,
            tipo=vehicle.tipo,
            color=vehicle.color,
            vin=vehicle.vin,
            combustible=vehicle.combustible,
            kilometraje=vehicle.kilometraje,
            propietario_rut=vehicle.propietario_rut,
            propietario_nombre=vehicle.propietario_nombre,
        )
    
    except BoostrNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con patente {patente} no encontrado",
        )
    except BoostrRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit excedido. Espere 1 minuto.",
        )
    except BoostrAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación con Boostr API",
        )
    except BoostrAPIError as e:
        logger.error(f"Error consultando vehículo {patente}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )


@router.get(
    "/vehiculo/{patente}/multas",
    response_model=List[TrafficFineResponse],
    summary="Consultar multas de un vehículo",
)
async def get_vehicle_fines(
    patente: str,
    client: BoostrClient = Depends(get_boostr),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Consulta las multas de tránsito de un vehículo.
    
    Útil para detectar ubicaciones donde ha estado el vehículo.
    
    **Consume 1 crédito de Boostr.**
    """
    try:
        fines = await client.get_traffic_fines(patente)
        
        return [
            TrafficFineResponse(
                juzgado=f.juzgado,
                comuna=f.comuna,
                rol=f.rol,
                año=f.año,
                fecha=f.fecha,
                estado=f.estado,
                monto=f.monto,
            )
            for f in fines
        ]
    
    except BoostrRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit excedido. Espere 1 minuto.",
        )
    except BoostrAPIError as e:
        logger.error(f"Error consultando multas de {patente}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )


# =============================================================================
# ENDPOINTS DE PERSONAS (RUTIFICADOR)
# =============================================================================

@router.get(
    "/persona/{rut}",
    response_model=PersonInfoResponse,
    summary="Consultar persona por RUT",
    responses={
        404: {"model": BoostrErrorResponse, "description": "Persona no encontrada"},
    },
)
async def get_person_info(
    rut: str,
    client: BoostrClient = Depends(get_boostr),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Consulta información de una persona por su RUT.
    
    Datos obtenidos:
    - Nombre completo
    - Género, nacionalidad
    - Fecha de nacimiento, edad
    - Estado de defunción
    
    **Consume 1 crédito de Boostr.**
    """
    try:
        person = await client.get_person_info(rut)
        
        return PersonInfoResponse(
            rut=person.rut,
            nombre=person.nombre,
            nombres=person.nombres,
            apellido_paterno=person.apellido_paterno,
            apellido_materno=person.apellido_materno,
            genero=person.genero,
            nacionalidad=person.nacionalidad,
            fecha_nacimiento=person.fecha_nacimiento,
            edad=person.edad,
            fallecido=person.fallecido,
        )
    
    except BoostrNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona con RUT {rut} no encontrada",
        )
    except BoostrValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RUT inválido: {rut}",
        )
    except BoostrRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit excedido. Espere 1 minuto.",
        )
    except BoostrAPIError as e:
        logger.error(f"Error consultando persona {rut}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )


@router.get(
    "/persona/{rut}/vehiculos",
    response_model=List[PersonVehicleResponse],
    summary="Consultar vehículos de una persona",
)
async def get_person_vehicles(
    rut: str,
    client: BoostrClient = Depends(get_boostr),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Consulta los vehículos registrados a nombre de una persona.
    
    Datos directamente del Registro de Vehículos Motorizados.
    
    **Consume 1 crédito de Boostr.**
    """
    try:
        vehicles = await client.get_person_vehicles(rut)
        
        return [
            PersonVehicleResponse(
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
            detail="Rate limit excedido. Espere 1 minuto.",
        )
    except BoostrAPIError as e:
        logger.error(f"Error consultando vehículos de {rut}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )


# =============================================================================
# ENDPOINTS DE INVESTIGACIÓN (COMBINADOS + REGISTRO)
# =============================================================================

@router.post(
    "/investigar/vehiculo/{patente}",
    response_model=InvestigacionVehiculoResponse,
    summary="Investigación completa de vehículo",
    status_code=status.HTTP_200_OK,
)
async def investigar_vehiculo(
    patente: str,
    oficio_id: Optional[int] = Query(None, description="ID del oficio para registrar la actividad"),
    incluir_multas: bool = Query(True, description="Incluir consulta de multas"),
    client: BoostrClient = Depends(get_boostr),
    repository: InvestigacionRepository = Depends(get_investigacion_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Realiza una investigación completa de un vehículo.
    
    Consulta:
    - Información del vehículo (patente, marca, modelo, etc.)
    - Multas de tránsito (ubicaciones)
    
    Si se proporciona `oficio_id`, registra la consulta en el timeline.
    
    **Consume 1-2 créditos de Boostr según las opciones.**
    """
    try:
        result = await client.investigar_vehiculo(
            patente=patente,
            incluir_multas=incluir_multas,
            incluir_revision=False,  # Ahorramos créditos
            incluir_soap=False,
        )
        
        # Registrar en el timeline si se proporciona oficio_id
        if oficio_id:
            try:
                use_case = AddActividadUseCase(repository)
                
                # Preparar datos para el JSON
                datos = {
                    "vehiculo": result.vehiculo.model_dump() if result.vehiculo else None,
                    "multas": [m.model_dump() for m in result.multas],
                    "creditos_usados": result.creditos_usados,
                }
                
                dto = CreateActividadDTO(
                    oficio_id=oficio_id,
                    tipo_actividad=TipoActividadEnum.CONSULTA_API,
                    descripcion=f"Consulta Boostr: Vehículo {patente}",
                    investigador_id=current_user.id,
                    resultado=f"Vehículo: {result.vehiculo.marca} {result.vehiculo.modelo}" if result.vehiculo else "Sin información",
                    api_externa="boostr",
                    datos_json=json.dumps(datos, default=str),
                )
                
                await use_case.execute(dto)
                logger.info(f"Actividad registrada para oficio {oficio_id}")
            
            except Exception as e:
                logger.error(f"Error registrando actividad: {e}")
                # No fallar la consulta si falla el registro
        
        # Preparar respuesta
        vehiculo_response = None
        if result.vehiculo:
            vehiculo_response = VehicleInfoResponse(
                patente=result.vehiculo.patente,
                marca=result.vehiculo.marca,
                modelo=result.vehiculo.modelo,
                año=result.vehiculo.año,
                tipo=result.vehiculo.tipo,
                color=result.vehiculo.color,
                vin=result.vehiculo.vin,
                combustible=result.vehiculo.combustible,
                kilometraje=result.vehiculo.kilometraje,
                propietario_rut=result.vehiculo.propietario_rut,
                propietario_nombre=result.vehiculo.propietario_nombre,
            )
        
        multas_response = [
            TrafficFineResponse(
                juzgado=m.juzgado,
                comuna=m.comuna,
                rol=m.rol,
                año=m.año,
                fecha=m.fecha,
                estado=m.estado,
                monto=m.monto,
            )
            for m in result.multas
        ]
        
        return InvestigacionVehiculoResponse(
            vehiculo=vehiculo_response,
            multas=multas_response,
            creditos_usados=result.creditos_usados,
            fecha_consulta=result.fecha_consulta,
        )
    
    except BoostrRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit excedido. Espere 1 minuto.",
        )
    except BoostrAPIError as e:
        logger.error(f"Error en investigación de vehículo {patente}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )


@router.post(
    "/investigar/propietario/{rut}",
    response_model=InvestigacionPropietarioResponse,
    summary="Investigación completa de propietario",
    status_code=status.HTTP_200_OK,
)
async def investigar_propietario(
    rut: str,
    oficio_id: Optional[int] = Query(None, description="ID del oficio para registrar la actividad"),
    incluir_vehiculos: bool = Query(True, description="Incluir otros vehículos"),
    client: BoostrClient = Depends(get_boostr),
    repository: InvestigacionRepository = Depends(get_investigacion_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Realiza una investigación completa de un propietario.
    
    Consulta:
    - Información de la persona (nombre, género, nacionalidad, etc.)
    - Otros vehículos a su nombre
    
    Si se proporciona `oficio_id`, registra la consulta en el timeline.
    
    **Consume 1-2 créditos de Boostr según las opciones.**
    """
    try:
        result = await client.investigar_propietario(
            rut=rut,
            incluir_vehiculos=incluir_vehiculos,
            incluir_propiedades=False,  # Ahorramos créditos
            incluir_verificaciones=False,
        )
        
        # Registrar en el timeline si se proporciona oficio_id
        if oficio_id:
            try:
                use_case = AddActividadUseCase(repository)
                
                # Preparar datos para el JSON
                datos = {
                    "propietario": result.propietario.model_dump() if result.propietario else None,
                    "otros_vehiculos": [v.model_dump() for v in result.otros_vehiculos],
                    "creditos_usados": result.creditos_usados,
                }
                
                dto = CreateActividadDTO(
                    oficio_id=oficio_id,
                    tipo_actividad=TipoActividadEnum.CONSULTA_API,
                    descripcion=f"Consulta Boostr: Propietario {rut}",
                    investigador_id=current_user.id,
                    resultado=f"Propietario: {result.propietario.nombre}" if result.propietario else "Sin información",
                    api_externa="boostr",
                    datos_json=json.dumps(datos, default=str),
                )
                
                await use_case.execute(dto)
                logger.info(f"Actividad registrada para oficio {oficio_id}")
            
            except Exception as e:
                logger.error(f"Error registrando actividad: {e}")
        
        # Preparar respuesta
        propietario_response = None
        if result.propietario:
            propietario_response = PersonInfoResponse(
                rut=result.propietario.rut,
                nombre=result.propietario.nombre,
                nombres=result.propietario.nombres,
                apellido_paterno=result.propietario.apellido_paterno,
                apellido_materno=result.propietario.apellido_materno,
                genero=result.propietario.genero,
                nacionalidad=result.propietario.nacionalidad,
                fecha_nacimiento=result.propietario.fecha_nacimiento,
                edad=result.propietario.edad,
                fallecido=result.propietario.fallecido,
            )
        
        vehiculos_response = [
            PersonVehicleResponse(
                patente=v.patente,
                marca=v.marca,
                modelo=v.modelo,
                año=v.año,
                tipo=v.tipo,
            )
            for v in result.otros_vehiculos
        ]
        
        return InvestigacionPropietarioResponse(
            propietario=propietario_response,
            vehiculos=vehiculos_response,
            creditos_usados=result.creditos_usados,
            fecha_consulta=result.fecha_consulta,
        )
    
    except BoostrValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RUT inválido: {rut}",
        )
    except BoostrRateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit excedido. Espere 1 minuto.",
        )
    except BoostrAPIError as e:
        logger.error(f"Error en investigación de propietario {rut}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error en servicio externo: {str(e)}",
        )
