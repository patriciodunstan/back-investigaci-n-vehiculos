"""
Router de buffets.

Endpoints CRUD para gestion de buffets.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db
from src.modules.buffets.application.dtos import CreateBuffetDTO, UpdateBuffetDTO
from src.modules.buffets.application.use_cases import (
    CreateBuffetUseCase,
    GetBuffetUseCase,
    UpdateBuffetUseCase,
    DeleteBuffetUseCase,
)
from src.modules.buffets.infrastructure.repositories import BuffetRepository
from src.modules.buffets.domain.exceptions import (
    BuffetNotFoundException,
    RutAlreadyExistsException,
)
from src.modules.buffets.presentation.schemas import (
    CreateBuffetRequest,
    UpdateBuffetRequest,
    BuffetResponse,
    BuffetListResponse,
)
from src.modules.usuarios.presentation.routers import get_current_user
from src.modules.usuarios.presentation.schemas import UserResponse


router = APIRouter(prefix="/buffets", tags=["Buffets"])


def get_buffet_repository(db: AsyncSession = Depends(get_db)) -> BuffetRepository:
    """Dependency para obtener el repositorio de buffets."""
    return BuffetRepository(db)


@router.get(
    "",
    response_model=BuffetListResponse,
    summary="Listar buffets",
)
async def list_buffets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    activo_only: bool = Query(True),
    repository: BuffetRepository = Depends(get_buffet_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Lista todos los buffets con paginacion."""
    use_case = GetBuffetUseCase(repository)
    buffets = await use_case.execute_list(skip=skip, limit=limit, activo_only=activo_only)
    total = await repository.count(activo_only=activo_only)

    return BuffetListResponse(
        items=[
            BuffetResponse(
                id=b.id,
                nombre=b.nombre,
                rut=b.rut,
                email_principal=b.email_principal,
                telefono=b.telefono,
                contacto_nombre=b.contacto_nombre,
                token_tablero=b.token_tablero,
                activo=b.activo,
                created_at=b.created_at,
                updated_at=b.updated_at,
            )
            for b in buffets
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{buffet_id}",
    response_model=BuffetResponse,
    summary="Obtener buffet",
)
async def get_buffet(
    buffet_id: int,
    repository: BuffetRepository = Depends(get_buffet_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Obtiene un buffet por ID."""
    use_case = GetBuffetUseCase(repository)
    try:
        buffet = await use_case.execute_by_id(buffet_id)
        return BuffetResponse(
            id=buffet.id,
            nombre=buffet.nombre,
            rut=buffet.rut,
            email_principal=buffet.email_principal,
            telefono=buffet.telefono,
            contacto_nombre=buffet.contacto_nombre,
            token_tablero=buffet.token_tablero,
            activo=buffet.activo,
            created_at=buffet.created_at,
            updated_at=buffet.updated_at,
        )
    except BuffetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post(
    "",
    response_model=BuffetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear buffet",
)
async def create_buffet(
    request: CreateBuffetRequest,
    repository: BuffetRepository = Depends(get_buffet_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Crea un nuevo buffet."""
    # Solo admin puede crear buffets
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear buffets",
        )

    use_case = CreateBuffetUseCase(repository)

    dto = CreateBuffetDTO(
        nombre=request.nombre,
        rut=request.rut,
        email_principal=request.email_principal,
        telefono=request.telefono,
        contacto_nombre=request.contacto_nombre,
    )

    try:
        buffet = await use_case.execute(dto)
        return BuffetResponse(
            id=buffet.id,
            nombre=buffet.nombre,
            rut=buffet.rut,
            email_principal=buffet.email_principal,
            telefono=buffet.telefono,
            contacto_nombre=buffet.contacto_nombre,
            token_tablero=buffet.token_tablero,
            activo=buffet.activo,
            created_at=buffet.created_at,
            updated_at=buffet.updated_at,
        )
    except RutAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{buffet_id}",
    response_model=BuffetResponse,
    summary="Actualizar buffet",
)
async def update_buffet(
    buffet_id: int,
    request: UpdateBuffetRequest,
    repository: BuffetRepository = Depends(get_buffet_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Actualiza un buffet existente."""
    use_case = UpdateBuffetUseCase(repository)

    dto = UpdateBuffetDTO(
        nombre=request.nombre,
        email_principal=request.email_principal,
        telefono=request.telefono,
        contacto_nombre=request.contacto_nombre,
    )

    try:
        buffet = await use_case.execute(buffet_id, dto)
        return BuffetResponse(
            id=buffet.id,
            nombre=buffet.nombre,
            rut=buffet.rut,
            email_principal=buffet.email_principal,
            telefono=buffet.telefono,
            contacto_nombre=buffet.contacto_nombre,
            token_tablero=buffet.token_tablero,
            activo=buffet.activo,
            created_at=buffet.created_at,
            updated_at=buffet.updated_at,
        )
    except BuffetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete(
    "/{buffet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar buffet",
)
async def delete_buffet(
    buffet_id: int,
    repository: BuffetRepository = Depends(get_buffet_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Desactiva un buffet (soft delete)."""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar buffets",
        )

    use_case = DeleteBuffetUseCase(repository)
    try:
        await use_case.execute(buffet_id)
    except BuffetNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
