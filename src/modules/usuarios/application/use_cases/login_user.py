"""
Caso de uso: Login de Usuario.

Principios aplicados:
- SRP: Solo maneja login
- DIP: Depende de abstracciones
"""

from src.modules.usuarios.application.dtos import LoginDTO, TokenResponseDTO
from src.modules.usuarios.application.interfaces import IUsuarioRepository
from src.modules.usuarios.domain.exceptions import (
    InvalidCredentialsException,
    InactiveUserException,
)
from src.modules.usuarios.infrastructure.services import password_hasher, jwt_service
from src.core.config import get_settings


class LoginUserUseCase:
    """
    Caso de uso para autenticar un usuario.

    Verifica credenciales y genera token JWT.
    """

    def __init__(self, repository: IUsuarioRepository):
        self._repository = repository

    async def execute(self, dto: LoginDTO) -> TokenResponseDTO:
        """
        Ejecuta el login de usuario.

        Args:
            dto: Credenciales de login

        Returns:
            TokenResponseDTO con el token JWT

        Raises:
            InvalidCredentialsException: Si email o password son incorrectos
            InactiveUserException: Si el usuario esta inactivo
        """
        # Buscar usuario por email
        usuario = await self._repository.get_by_email(dto.email)

        if usuario is None:
            raise InvalidCredentialsException()

        # Verificar contrasena
        if not password_hasher.verify(dto.password, usuario.password_hash):
            raise InvalidCredentialsException()

        # Verificar que este activo
        if not usuario.activo:
            raise InactiveUserException(dto.email)

        # Generar token
        settings = get_settings()
        token = jwt_service.create_access_token(
            user_id=usuario.id,
            email=usuario.email_str,
            rol=usuario.rol,
            buffet_id=usuario.buffet_id,
        )

        return TokenResponseDTO(
            access_token=token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # en segundos
        )
