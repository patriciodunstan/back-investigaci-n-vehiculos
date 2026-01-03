"""
Caso de uso: Crear Buffet.
"""

from src.modules.buffets.application.dtos import CreateBuffetDTO, BuffetResponseDTO
from src.modules.buffets.application.interfaces import IBuffetRepository
from src.modules.buffets.domain.entities import Buffet
from src.modules.buffets.domain.exceptions import RutAlreadyExistsException


class CreateBuffetUseCase:
    """Caso de uso para crear un nuevo buffet."""

    def __init__(self, repository: IBuffetRepository):
        self._repository = repository

    async def execute(self, dto: CreateBuffetDTO) -> BuffetResponseDTO:
        """
        Ejecuta la creacion de buffet.

        Args:
            dto: Datos del buffet a crear

        Returns:
            BuffetResponseDTO con datos del buffet creado

        Raises:
            RutAlreadyExistsException: Si el RUT ya existe
        """
        # Verificar que el RUT no exista
        if await self._repository.exists_by_rut(dto.rut):
            raise RutAlreadyExistsException(dto.rut)

        # Crear entidad de dominio
        buffet = Buffet.crear(
            nombre=dto.nombre,
            rut=dto.rut,
            email_principal=dto.email_principal,
            telefono=dto.telefono,
            contacto_nombre=dto.contacto_nombre,
        )

        # Persistir
        buffet_creado = await self._repository.add(buffet)

        return BuffetResponseDTO.from_entity(buffet_creado)
