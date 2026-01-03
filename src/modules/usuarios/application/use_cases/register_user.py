"""
Caso de uso: Registrar Usuario.

Principios aplicados:
- SRP: Solo registra usuarios
- DIP: Depende de abstracciones (IUsuarioRepository)
"""

from src.modules.usuarios.application.dtos import RegisterUserDTO, UserResponseDTO
from src.modules.usuarios.application.interfaces import IUsuarioRepository
from src.modules.usuarios.domain.entities import Usuario
from src.modules.usuarios.domain.exceptions import EmailAlreadyExistsException
from src.modules.usuarios.infrastructure.services import password_hasher


class RegisterUserUseCase:
    """
    Caso de uso para registrar un nuevo usuario.

    Valida que el email no exista, hashea la contrasena
    y crea el usuario en el sistema.
    """

    def __init__(self, repository: IUsuarioRepository):
        self._repository = repository

    async def execute(self, dto: RegisterUserDTO) -> UserResponseDTO:
        """
        Ejecuta el registro de usuario.

        Args:
            dto: Datos del usuario a registrar

        Returns:
            UserResponseDTO con datos del usuario creado

        Raises:
            EmailAlreadyExistsException: Si el email ya existe
            ValueError: Si los datos son invalidos
        """
        # Verificar que el email no exista
        if await self._repository.exists_by_email(dto.email):
            raise EmailAlreadyExistsException(dto.email)

        # Hashear contrasena
        hashed_password = password_hasher.hash(dto.password)

        # Crear entidad de dominio
        usuario = Usuario.crear(
            email=dto.email,
            nombre=dto.nombre,
            password_hash=hashed_password,
            rol=dto.rol,
            buffet_id=dto.buffet_id,
        )

        # Persistir
        usuario_creado = await self._repository.add(usuario)

        # Retornar DTO de respuesta
        return UserResponseDTO.from_entity(usuario_creado)
