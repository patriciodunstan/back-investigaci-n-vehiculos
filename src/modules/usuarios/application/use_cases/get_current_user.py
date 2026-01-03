"""
Caso de uso: Obtener Usuario Actual.

Principios aplicados:
- SRP: Solo obtiene el usuario actual desde token
- DIP: Depende de abstracciones
"""

from src.modules.usuarios.application.dtos import UserResponseDTO
from src.modules.usuarios.application.interfaces import IUsuarioRepository
from src.modules.usuarios.domain.exceptions import (
    InvalidTokenException,
    UsuarioNotFoundException,
    InactiveUserException,
)
from src.modules.usuarios.infrastructure.services import jwt_service


class GetCurrentUserUseCase:
    """
    Caso de uso para obtener el usuario actual desde un token.

    Decodifica el token y retorna los datos del usuario.
    """

    def __init__(self, repository: IUsuarioRepository):
        self._repository = repository

    async def execute(self, token: str) -> UserResponseDTO:
        """
        Obtiene el usuario actual desde el token.

        Args:
            token: Token JWT

        Returns:
            UserResponseDTO con datos del usuario

        Raises:
            InvalidTokenException: Si el token es invalido o expiro
            UsuarioNotFoundException: Si el usuario no existe
            InactiveUserException: Si el usuario esta inactivo
        """
        # Decodificar token
        payload = jwt_service.decode_token(token)
        if payload is None:
            raise InvalidTokenException()

        # Extraer user_id
        user_id = jwt_service.get_user_id_from_token(token)
        if user_id is None:
            raise InvalidTokenException("Token no contiene user_id valido")

        # Buscar usuario
        usuario = await self._repository.get_by_id(user_id)
        if usuario is None:
            raise UsuarioNotFoundException(user_id)

        # Verificar que este activo
        if not usuario.activo:
            raise InactiveUserException(usuario.email_str)

        return UserResponseDTO.from_entity(usuario)

    async def execute_from_user_id(self, user_id: int) -> UserResponseDTO:
        """
        Obtiene el usuario desde su ID directamente.

        Args:
            user_id: ID del usuario

        Returns:
            UserResponseDTO con datos del usuario
        """
        usuario = await self._repository.get_by_id(user_id)
        if usuario is None:
            raise UsuarioNotFoundException(user_id)

        if not usuario.activo:
            raise InactiveUserException(usuario.email_str)

        return UserResponseDTO.from_entity(usuario)
