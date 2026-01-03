"""
Dependencies de paginación.

Proporciona parámetros comunes de paginación para endpoints de listado.

Principios aplicados:
- DRY: Lógica de paginación en un solo lugar
"""

from fastapi import Query
from dataclasses import dataclass

from src.core.config import get_settings

settings = get_settings()


@dataclass
class PaginationParams:
    """
    Parámetros de paginación.

    Attributes:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
    """

    skip: int
    limit: int

    @property
    def offset(self) -> int:
        """Alias para skip (más común en SQL)"""
        return self.skip


def get_pagination(
    skip: int = Query(default=0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(
        default=None,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description=f"Número máximo de registros (máx: {settings.MAX_PAGE_SIZE})",
    ),
) -> PaginationParams:
    """
    Dependency para obtener parámetros de paginación.

    Uso en endpoints:
        @router.get("/items")
        async def list_items(
            pagination: PaginationParams = Depends(get_pagination)
        ):
            items = db.query(Item).offset(pagination.skip).limit(pagination.limit).all()
            return items

    Args:
        skip: Registros a saltar (default: 0)
        limit: Máximo de registros (default: DEFAULT_PAGE_SIZE)

    Returns:
        PaginationParams: Objeto con skip y limit validados
    """
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE

    return PaginationParams(skip=skip, limit=limit)
