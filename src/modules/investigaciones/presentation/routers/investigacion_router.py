"""
Router de investigaciones.

Endpoints para timeline, actividades y avistamientos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.shared.infrastructure.database import get_db
from src.modules.investigaciones.application.dtos import (
    CreateActividadDTO,
    CreateAvistamientoDTO,
)
from src.modules.investigaciones.application.use_cases import (
    AddActividadUseCase,
    AddAvistamientoUseCase,
    GetTimelineUseCase,
)
from src.modules.investigaciones.infrastructure.repositories import (
    InvestigacionRepository,
)
from src.modules.investigaciones.presentation.schemas import (
    CreateActividadRequest,
    CreateAvistamientoRequest,
    ActividadResponse,
    AvistamientoResponse,
    TimelineItemResponse,
    TimelineResponse,
)
from src.modules.usuarios.presentation.routers import get_current_user
from src.modules.usuarios.presentation.schemas import UserResponse


router = APIRouter(tags=["Investigaciones"])


def get_investigacion_repository(
    db: Session = Depends(get_db),
) -> InvestigacionRepository:
    """Dependency para obtener el repositorio."""
    return InvestigacionRepository(db)


@router.get(
    "/oficios/{oficio_id}/timeline",
    response_model=TimelineResponse,
    summary="Obtener timeline",
)
async def get_timeline(
    oficio_id: int,
    limit: int = Query(50, ge=1, le=200),
    repository: InvestigacionRepository = Depends(get_investigacion_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Obtiene el timeline de un oficio con actividades y avistamientos."""
    use_case = GetTimelineUseCase(repository)
    items = await use_case.execute(oficio_id, limit)

    return TimelineResponse(
        oficio_id=oficio_id,
        items=[
            TimelineItemResponse(
                tipo=item.tipo,
                id=item.id,
                fecha=item.fecha,
                descripcion=item.descripcion,
                detalle=item.detalle,
                fuente=item.fuente,
                investigador_id=item.investigador_id,
            )
            for item in items
        ],
        total=len(items),
    )


@router.post(
    "/oficios/{oficio_id}/actividades",
    response_model=ActividadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar actividad",
)
async def add_actividad(
    oficio_id: int,
    request: CreateActividadRequest,
    repository: InvestigacionRepository = Depends(get_investigacion_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Agrega una actividad al timeline."""
    use_case = AddActividadUseCase(repository)

    dto = CreateActividadDTO(
        oficio_id=oficio_id,
        tipo_actividad=request.tipo_actividad,
        descripcion=request.descripcion,
        investigador_id=current_user.id,
        resultado=request.resultado,
        api_externa=request.api_externa,
        datos_json=request.datos_json,
    )

    result = await use_case.execute(dto)

    return ActividadResponse(
        id=result.id,
        oficio_id=result.oficio_id,
        investigador_id=result.investigador_id,
        tipo_actividad=result.tipo_actividad,
        descripcion=result.descripcion,
        resultado=result.resultado,
        api_externa=result.api_externa,
        datos_json=result.datos_json,
        fecha_actividad=result.fecha_actividad,
        created_at=result.created_at,
    )


@router.post(
    "/oficios/{oficio_id}/avistamientos",
    response_model=AvistamientoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar avistamiento",
)
async def add_avistamiento(
    oficio_id: int,
    request: CreateAvistamientoRequest,
    repository: InvestigacionRepository = Depends(get_investigacion_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Registra un avistamiento del vehiculo."""
    use_case = AddAvistamientoUseCase(repository)

    dto = CreateAvistamientoDTO(
        oficio_id=oficio_id,
        fuente=request.fuente,
        ubicacion=request.ubicacion,
        fecha_hora=request.fecha_hora,
        latitud=request.latitud,
        longitud=request.longitud,
        notas=request.notas,
    )

    result = await use_case.execute(dto)

    return AvistamientoResponse(
        id=result.id,
        oficio_id=result.oficio_id,
        fuente=result.fuente,
        fecha_hora=result.fecha_hora,
        ubicacion=result.ubicacion,
        latitud=result.latitud,
        longitud=result.longitud,
        api_response_id=result.api_response_id,
        datos_json=result.datos_json,
        notas=result.notas,
        created_at=result.created_at,
    )

