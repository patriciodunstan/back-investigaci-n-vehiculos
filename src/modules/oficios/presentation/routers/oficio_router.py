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
from src.modules.oficios.infrastructure.repositories import OficioRepository
from src.modules.oficios.domain.exceptions import (
    OficioNotFoundException,
    NumeroOficioAlreadyExistsException,
)
from src.modules.oficios.presentation.schemas import (
    CreateOficioRequest,
    UpdateOficioRequest,
    AsignarInvestigadorRequest,
    CambiarEstadoRequest,
    PropietarioRequest,
    DireccionRequest,
    OficioResponse,
    OficioListResponse,
    PropietarioResponse,
    DireccionResponse,
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
    vehiculo = None
    if dto.vehiculo:
        vehiculo = VehiculoResponse(
            id=dto.vehiculo.id,
            patente=dto.vehiculo.patente,
            marca=dto.vehiculo.marca,
            modelo=dto.vehiculo.modelo,
            año=dto.vehiculo.año,
            color=dto.vehiculo.color,
            vin=dto.vehiculo.vin,
        )

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
        vehiculo=vehiculo,
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
            fecha_verificacion=result.fecha_verificacion,
            notas=result.notas,
        )
    except OficioNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
