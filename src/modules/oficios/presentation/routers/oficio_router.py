"""
Router de oficios.

Endpoints para gestion de oficios de investigacion.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.shared.infrastructure.database import get_db
from src.shared.domain.enums import EstadoOficioEnum, PrioridadEnum
from src.modules.oficios.application.dtos import (
    CreateOficioDTO,
    UpdateOficioDTO,
    AsignarInvestigadorDTO,
    CambiarEstadoDTO,
    PropietarioDTO,
    DireccionDTO,
    VehiculoDTO,
    VisitaDireccionDTO,
)
from src.modules.oficios.application.use_cases import (
    CreateOficioUseCase,
    GetOficioUseCase,
    UpdateOficioUseCase,
    AsignarInvestigadorUseCase,
    CambiarEstadoUseCase,
    AgregarPropietarioUseCase,
    AgregarDireccionUseCase,
)
from src.modules.oficios.application.use_cases.registrar_visita import (
    RegistrarVisitaUseCase,
    GetHistorialVisitasUseCase,
    GetDireccionesPendientesUseCase,
)
from src.modules.oficios.infrastructure.repositories import OficioRepository
from src.modules.oficios.domain.exceptions import (
    OficioNotFoundException,
    NumeroOficioAlreadyExistsException,
    DireccionNotFoundException,
)
from src.modules.oficios.presentation.schemas import (
    CreateOficioRequest,
    UpdateOficioRequest,
    AsignarInvestigadorRequest,
    CambiarEstadoRequest,
    PropietarioRequest,
    DireccionRequest,
    RegistrarVisitaRequest,
    OficioResponse,
    OficioListResponse,
    PropietarioResponse,
    DireccionResponse,
    VisitaDireccionResponse,
    VehiculoResponse,
)
from src.modules.usuarios.presentation.routers import get_current_user
from src.modules.usuarios.presentation.schemas import UserResponse


router = APIRouter(prefix="/oficios", tags=["Oficios"])


def get_oficio_repository(db: Session = Depends(get_db)) -> OficioRepository:
    """Dependency para obtener el repositorio."""
    return OficioRepository(db)


def _dto_to_response(dto) -> OficioResponse:
    """Convierte DTO a response."""
    vehiculos = [
        VehiculoResponse(
            id=v.id,
            patente=v.patente,
            marca=v.marca,
            modelo=v.modelo,
            año=v.año,
            color=v.color,
            vin=v.vin,
        )
        for v in dto.vehiculos
    ]

    propietarios = [
        PropietarioResponse(
            id=p.id,
            rut=p.rut,
            nombre_completo=p.nombre_completo,
            tipo=p.tipo,
            email=p.email,
            telefono=p.telefono,
            direccion_principal=p.direccion_principal,
            notas=p.notas,
        )
        for p in dto.propietarios
    ]

    direcciones = [
        DireccionResponse(
            id=d.id,
            direccion=d.direccion,
            tipo=d.tipo,
            comuna=d.comuna,
            region=d.region,
            verificada=d.verificada,
            fecha_verificacion=d.fecha_verificacion,
            notas=d.notas,
        )
        for d in dto.direcciones
    ]

    return OficioResponse(
        id=dto.id,
        numero_oficio=dto.numero_oficio,
        buffet_id=dto.buffet_id,
        buffet_nombre=dto.buffet_nombre,
        investigador_id=dto.investigador_id,
        investigador_nombre=dto.investigador_nombre,
        estado=dto.estado,
        prioridad=dto.prioridad,
        fecha_ingreso=dto.fecha_ingreso,
        fecha_limite=dto.fecha_limite,
        notas_generales=dto.notas_generales,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        vehiculos=vehiculos,
        propietarios=propietarios,
        direcciones=direcciones,
    )


@router.get(
    "",
    response_model=OficioListResponse,
    summary="Listar oficios",
)
async def list_oficios(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    buffet_id: Optional[int] = Query(None),
    investigador_id: Optional[int] = Query(None),
    estado: Optional[EstadoOficioEnum] = Query(None),
    repository: OficioRepository = Depends(get_oficio_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Lista oficios con filtros."""
    # Si es cliente, solo ve oficios de su buffet
    if current_user.rol == "cliente" and current_user.buffet_id:
        buffet_id = current_user.buffet_id

    use_case = GetOficioUseCase(repository)
    oficios = await use_case.execute_list(
        skip=skip,
        limit=limit,
        buffet_id=buffet_id,
        investigador_id=investigador_id,
        estado=estado,
    )

    total = await repository.count(
        buffet_id=buffet_id,
        investigador_id=investigador_id,
        estado=estado,
    )

    return OficioListResponse(
        items=[_dto_to_response(o) for o in oficios],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{oficio_id}",
    response_model=OficioResponse,
    summary="Obtener oficio",
)
async def get_oficio(
    oficio_id: int,
    repository: OficioRepository = Depends(get_oficio_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Obtiene un oficio con todas sus relaciones."""
    use_case = GetOficioUseCase(repository)
    try:
        dto = await use_case.execute_by_id(oficio_id)
        return _dto_to_response(dto)
    except OficioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post(
    "",
    response_model=OficioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear oficio",
)
async def create_oficio(
    request: CreateOficioRequest,
    repository: OficioRepository = Depends(get_oficio_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Crea un nuevo oficio con vehiculo."""
    # Solo admin o investigador pueden crear
    if current_user.rol not in ("admin", "investigador"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear oficios",
        )

    use_case = CreateOficioUseCase(repository)

    vehiculo_dto = VehiculoDTO(
        patente=request.vehiculo.patente,
        marca=request.vehiculo.marca,
        modelo=request.vehiculo.modelo,
        año=request.vehiculo.año,
        color=request.vehiculo.color,
        vin=request.vehiculo.vin,
    )
    dto = CreateOficioDTO(
        numero_oficio=request.numero_oficio,
        buffet_id=request.buffet_id,
        vehiculo=vehiculo_dto,
        prioridad=request.prioridad,
        fecha_limite=request.fecha_limite,
        notas_generales=request.notas_generales,
    )

    try:
        result = await use_case.execute(dto)
        return _dto_to_response(result)
    except NumeroOficioAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{oficio_id}",
    response_model=OficioResponse,
    summary="Actualizar oficio",
)
async def update_oficio(
    oficio_id: int,
    request: UpdateOficioRequest,
    repository: OficioRepository = Depends(get_oficio_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Actualiza un oficio."""
    use_case = UpdateOficioUseCase(repository)

    dto = UpdateOficioDTO(
        prioridad=request.prioridad,
        fecha_limite=request.fecha_limite,
        notas_generales=request.notas_generales,
    )

    try:
        result = await use_case.execute(oficio_id, dto)
        return _dto_to_response(result)
    except OficioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.patch(
    "/{oficio_id}/asignar",
    response_model=OficioResponse,
    summary="Asignar investigador",
)
async def asignar_investigador(
    oficio_id: int,
    request: AsignarInvestigadorRequest,
    repository: OficioRepository = Depends(get_oficio_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Asigna un investigador al oficio."""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin puede asignar investigadores",
        )

    use_case = AsignarInvestigadorUseCase(repository)
    dto = AsignarInvestigadorDTO(investigador_id=request.investigador_id)

    try:
        result = await use_case.execute(oficio_id, dto)
        return _dto_to_response(result)
    except OficioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.patch(
    "/{oficio_id}/estado",
    response_model=OficioResponse,
    summary="Cambiar estado",
)
async def cambiar_estado(
    oficio_id: int,
    request: CambiarEstadoRequest,
    repository: OficioRepository = Depends(get_oficio_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Cambia el estado del oficio."""
    use_case = CambiarEstadoUseCase(repository)
    dto = CambiarEstadoDTO(estado=request.estado)

    try:
        result = await use_case.execute(oficio_id, dto)
        return _dto_to_response(result)
    except OficioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post(
    "/{oficio_id}/propietarios",
    response_model=PropietarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar propietario",
)
async def add_propietario(
    oficio_id: int,
    request: PropietarioRequest,
    repository: OficioRepository = Depends(get_oficio_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Agrega un propietario al oficio."""
    use_case = AgregarPropietarioUseCase(repository)

    dto = PropietarioDTO(
        rut=request.rut,
        nombre_completo=request.nombre_completo,
        tipo=request.tipo,
        email=request.email,
        telefono=request.telefono,
        direccion_principal=request.direccion_principal,
        notas=request.notas,
    )

    try:
        result = await use_case.execute(oficio_id, dto)
        return PropietarioResponse(
            id=result.id,
            rut=result.rut,
            nombre_completo=result.nombre_completo,
            tipo=result.tipo,
            email=result.email,
            telefono=result.telefono,
            direccion_principal=result.direccion_principal,
            notas=result.notas,
        )
    except OficioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post(
    "/{oficio_id}/direcciones",
    response_model=DireccionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar direccion",
)
async def add_direccion(
    oficio_id: int,
    request: DireccionRequest,
    repository: OficioRepository = Depends(get_oficio_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Agrega una direccion al oficio."""
    use_case = AgregarDireccionUseCase(repository)

    dto = DireccionDTO(
        direccion=request.direccion,
        tipo=request.tipo,
        comuna=request.comuna,
        region=request.region,
        notas=request.notas,
    )

    try:
        result = await use_case.execute(
            oficio_id,
            dto,
            agregada_por_id=current_user.id,
        )
        return DireccionResponse(
            id=result.id,
            direccion=result.direccion,
            tipo=result.tipo,
            comuna=result.comuna,
            region=result.region,
            verificada=result.verificada,
            resultado_verificacion=result.resultado_verificacion,
            fecha_verificacion=result.fecha_verificacion,
            verificada_por_id=result.verificada_por_id,
            verificada_por_nombre=result.verificada_por_nombre,
            cantidad_visitas=result.cantidad_visitas,
            notas=result.notas,
        )
    except OficioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# =============================================================================
# ENDPOINTS DE VISITAS A DIRECCIONES
# =============================================================================

@router.post(
    "/direcciones/{direccion_id}/visitas",
    response_model=VisitaDireccionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar visita a dirección",
)
async def registrar_visita(
    direccion_id: int,
    request: RegistrarVisitaRequest,
    repository: OficioRepository = Depends(get_oficio_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Registra una visita a una dirección.
    
    Actualiza el estado de verificación de la dirección y guarda
    la visita en el historial.
    
    Resultados posibles:
    - `exitosa`: Se encontró al propietario/vehículo
    - `no_encontrado`: Nadie en el domicilio
    - `direccion_incorrecta`: La dirección no existe o es errónea
    - `se_mudo`: El propietario ya no vive ahí
    - `rechazo_atencion`: Se negaron a atender
    - `otro`: Otro resultado
    """
    use_case = RegistrarVisitaUseCase(repository)

    dto = VisitaDireccionDTO(
        resultado=request.resultado,
        notas=request.notas,
        latitud=request.latitud,
        longitud=request.longitud,
    )

    try:
        result = await use_case.execute(
            direccion_id=direccion_id,
            dto=dto,
            investigador_id=current_user.id,
        )
        return VisitaDireccionResponse(
            id=result.id,
            direccion_id=result.direccion_id,
            investigador_id=result.investigador_id,
            investigador_nombre=result.investigador_nombre,
            fecha_visita=result.fecha_visita,
            resultado=result.resultado,
            notas=result.notas,
            latitud=result.latitud,
            longitud=result.longitud,
        )
    except DireccionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/direcciones/{direccion_id}/visitas",
    response_model=list[VisitaDireccionResponse],
    summary="Historial de visitas a dirección",
)
async def get_historial_visitas(
    direccion_id: int,
    repository: OficioRepository = Depends(get_oficio_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Obtiene el historial de visitas a una dirección.
    
    Retorna todas las visitas ordenadas por fecha (más reciente primero).
    """
    use_case = GetHistorialVisitasUseCase(repository)

    try:
        visitas = await use_case.execute(direccion_id)
        return [
            VisitaDireccionResponse(
                id=v.id,
                direccion_id=v.direccion_id,
                investigador_id=v.investigador_id,
                investigador_nombre=v.investigador_nombre,
                fecha_visita=v.fecha_visita,
                resultado=v.resultado,
                notas=v.notas,
                latitud=v.latitud,
                longitud=v.longitud,
            )
            for v in visitas
        ]
    except DireccionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{oficio_id}/direcciones/pendientes",
    response_model=list[DireccionResponse],
    summary="Direcciones pendientes de verificar",
)
async def get_direcciones_pendientes(
    oficio_id: int,
    repository: OficioRepository = Depends(get_oficio_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """
    Obtiene las direcciones de un oficio que requieren verificación.
    
    Incluye:
    - Direcciones nunca visitadas (pendiente)
    - Direcciones con resultado no_encontrado (intentar de nuevo)
    - Direcciones con rechazo de atención (intentar de nuevo)
    """
    use_case = GetDireccionesPendientesUseCase(repository)
    direcciones = await use_case.execute(oficio_id)
    
    return [
        DireccionResponse(
            id=d.id,
            direccion=d.direccion,
            tipo=d.tipo,
            comuna=d.comuna,
            region=d.region,
            verificada=d.verificada,
            resultado_verificacion=d.resultado_verificacion,
            fecha_verificacion=d.fecha_verificacion,
            verificada_por_id=d.verificada_por_id,
            verificada_por_nombre=d.verificada_por_nombre,
            cantidad_visitas=d.cantidad_visitas,
            notas=d.notas,
        )
        for d in direcciones
    ]
