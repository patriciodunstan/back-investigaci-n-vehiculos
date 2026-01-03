"""
Caso de uso: Actualizar Buffet.
"""

from src.modules.buffets.application.dtos import UpdateBuffetDTO, BuffetResponseDTO
from src.modules.buffets.application.interfaces import IBuffetRepository
from src.modules.buffets.domain.exceptions import BuffetNotFoundException


class UpdateBuffetUseCase:
    """Caso de uso para actualizar un buffet."""

    def __init__(self, repository: IBuffetRepository):
        self._repository = repository

    async def execute(
        self,
        buffet_id: int,
        dto: UpdateBuffetDTO,
    ) -> BuffetResponseDTO:
        """
        Actualiza un buffet.

        Args:
            buffet_id: ID del buffet
            dto: Datos a actualizar

        Returns:
            BuffetResponseDTO con datos actualizados
        """
        buffet = await self._repository.get_by_id(buffet_id)
        if buffet is None:
            raise BuffetNotFoundException(buffet_id)

        buffet.actualizar(
            nombre=dto.nombre,
            email_principal=dto.email_principal,
            telefono=dto.telefono,
            contacto_nombre=dto.contacto_nombre,
        )

        buffet_actualizado = await self._repository.update(buffet)

        return BuffetResponseDTO.from_entity(buffet_actualizado)


class DeleteBuffetUseCase:
    """Caso de uso para desactivar un buffet."""

    def __init__(self, repository: IBuffetRepository):
        self._repository = repository

    async def execute(self, buffet_id: int) -> bool:
        """Desactiva un buffet (soft delete)."""
        buffet = await self._repository.get_by_id(buffet_id)
        if buffet is None:
            raise BuffetNotFoundException(buffet_id)

        return await self._repository.delete(buffet_id)
