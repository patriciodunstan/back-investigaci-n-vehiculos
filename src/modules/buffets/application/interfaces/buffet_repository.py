"""
Interface del repositorio de buffets.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.buffets.domain.entities import Buffet


class IBuffetRepository(ABC):
    """Interface para el repositorio de buffets."""

    @abstractmethod
    async def get_by_id(self, buffet_id: int) -> Optional[Buffet]:
        """Obtiene un buffet por su ID."""
        pass

    @abstractmethod
    async def get_by_rut(self, rut: str) -> Optional[Buffet]:
        """Obtiene un buffet por su RUT."""
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[Buffet]:
        """Obtiene un buffet por su token de tablero."""
        pass

    @abstractmethod
    async def exists_by_rut(self, rut: str) -> bool:
        """Verifica si existe un buffet con el RUT dado."""
        pass

    @abstractmethod
    async def add(self, buffet: Buffet) -> Buffet:
        """Agrega un nuevo buffet."""
        pass

    @abstractmethod
    async def update(self, buffet: Buffet) -> Buffet:
        """Actualiza un buffet existente."""
        pass

    @abstractmethod
    async def delete(self, buffet_id: int) -> bool:
        """Elimina un buffet (soft delete)."""
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        activo_only: bool = True,
    ) -> List[Buffet]:
        """Obtiene lista de buffets con paginacion."""
        pass

    @abstractmethod
    async def count(self, activo_only: bool = True) -> int:
        """Cuenta el total de buffets."""
        pass
