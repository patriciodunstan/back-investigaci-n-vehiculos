"""
Caso de uso: Obtener Buffet.
"""

from typing import List

from src.modules.buffets.application.dtos import BuffetResponseDTO
from src.modules.buffets.application.interfaces import IBuffetRepository
from src.modules.buffets.domain.exceptions import BuffetNotFoundException


class GetBuffetUseCase:
    """Caso de uso para obtener buffets."""

    def __init__(self, repository: IBuffetRepository):
        self._repository = repository

    async def execute_by_id(self, buffet_id: int) -> BuffetResponseDTO:
        """Obtiene un buffet por ID."""
        buffet = await self._repository.get_by_id(buffet_id)
        if buffet is None:
            raise BuffetNotFoundException(buffet_id)
        return BuffetResponseDTO.from_entity(buffet)

    async def execute_list(
        self,
        skip: int = 0,
        limit: int = 100,
        activo_only: bool = True,
    ) -> List[BuffetResponseDTO]:
        """Obtiene lista de buffets."""
        buffets = await self._repository.get_all(
            skip=skip,
            limit=limit,
            activo_only=activo_only,
        )
        return [BuffetResponseDTO.from_entity(b) for b in buffets]

    async def execute_by_token(self, token: str) -> BuffetResponseDTO:
        """Obtiene un buffet por token de tablero."""
        buffet = await self._repository.get_by_token(token)
        if buffet is None:
            raise BuffetNotFoundException(0)
        return BuffetResponseDTO.from_entity(buffet)
