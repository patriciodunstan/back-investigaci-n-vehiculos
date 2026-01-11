"""
Router de usuarios.

Endpoints para gestion de usuarios (listado, etc.).

Principios aplicados:
- SRP: Solo endpoints de gestion de usuarios (no autenticacion)
- Thin controller: Delega logica a repositorios
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.shared.infrastructure.database import get_db
from src.shared.domain.enums import RolEnum
from src.modules.usuarios.infrastructure.repositories import UsuarioRepository
from src.modules.usuarios.application.dtos import UserResponseDTO
from src.modules.usuarios.presentation.schemas import (
    UserResponse,
    UserListResponse,
)
from src.modules.usuarios.presentation.routers.auth_router import get_current_user


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def get_usuario_repository(db: AsyncSession = Depends(get_db)) -> UsuarioRepository:
    """Dependency para obtener el repositorio de usuarios."""
    return UsuarioRepository(db)


@router.get(
    "",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Obtiene una lista paginada de usuarios del sistema",
)
async def list_usuarios(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Maximo de registros"),
    activo_only: bool = Query(True, description="Solo usuarios activos"),
    rol: Optional[RolEnum] = Query(None, description="Filtrar por rol"),
    buffet_id: Optional[int] = Query(None, description="Filtrar por buffet"),
    repository: UsuarioRepository = Depends(get_usuario_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Lista usuarios del sistema con paginacion y filtros opcionales.

    - **skip**: Numero de registros a saltar (paginacion)
    - **limit**: Numero maximo de registros a retornar (max 100)
    - **activo_only**: Si solo incluir usuarios activos (default: true)
    - **rol**: Filtro opcional por rol (admin, investigador, cliente)
    - **buffet_id**: Filtro opcional por buffet

    Requiere autenticacion.
    """
    # Si se especifica buffet_id, usar metodo especifico
    if buffet_id is not None:
        usuarios = await repository.get_by_buffet(
            buffet_id=buffet_id,
            skip=skip,
            limit=limit,
        )
        # Contar usuarios del buffet (activos por defecto en get_by_buffet)
        total = len(usuarios)  # Simplificado, podria mejorarse con count_by_buffet
    else:
        # Listar todos los usuarios
        usuarios = await repository.get_all(
            skip=skip,
            limit=limit,
            activo_only=activo_only,
        )
        total = await repository.count(activo_only=activo_only)

    # Filtrar por rol si se especifica
    if rol is not None:
        usuarios = [u for u in usuarios if u.rol == rol]
        # Ajustar total después del filtro
        # Nota: Esto es una aproximación, para un conteo exacto se necesitaría
        # un método en el repositorio que cuente con filtros combinados
        total = len(usuarios)

    # Convertir entidades a DTOs y luego a schemas de respuesta
    items = [
        UserResponse(
            id=dto.id,
            email=dto.email,
            nombre=dto.nombre,
            rol=dto.rol,
            buffet_id=dto.buffet_id,
            activo=dto.activo,
            avatar_url=dto.avatar_url,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
        for dto in [UserResponseDTO.from_entity(u) for u in usuarios]
    ]

    return UserListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
