"""
Tests para RegisterUserUseCase.

Verifica el registro de usuarios con diferentes escenarios.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.usuarios.application.use_cases.register_user import RegisterUserUseCase
from src.modules.usuarios.application.dtos import RegisterUserDTO
from src.modules.usuarios.domain.entities import Usuario
from src.modules.usuarios.domain.exceptions import EmailAlreadyExistsException
from src.shared.domain.enums import RolEnum


class TestRegisterUserUseCase:
    """Tests para RegisterUserUseCase"""

    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio de usuarios"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        """Instancia del use case con mock"""
        return RegisterUserUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_register_user_exitoso(self, use_case, mock_repository, password_hasher):
        """Test registro exitoso de usuario"""
        # Arrange
        dto = RegisterUserDTO(
            email="nuevo@test.com",
            password="password123",
            nombre="Usuario Nuevo",
            rol=RolEnum.CLIENTE,
        )

        password_hash = password_hasher.hash(dto.password)
        usuario_creado = Usuario.crear(
            email=dto.email,
            nombre=dto.nombre,
            password_hash=password_hash,
            rol=dto.rol,
        )
        usuario_creado.id = 1

        mock_repository.exists_by_email.return_value = False
        mock_repository.add.return_value = usuario_creado

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.id == 1
        assert result.email == dto.email
        assert result.nombre == dto.nombre
        assert result.rol == dto.rol.value
        mock_repository.exists_by_email.assert_called_once_with(dto.email)
        mock_repository.add.assert_called_once()
        # Verificar que el password fue hasheado
        usuario_agregado = mock_repository.add.call_args[0][0]
        assert usuario_agregado.password_hash != dto.password
        assert password_hasher.verify(dto.password, usuario_agregado.password_hash)

    @pytest.mark.asyncio
    async def test_register_user_email_duplicado(self, use_case, mock_repository):
        """Test que lanza excepción cuando el email ya existe"""
        # Arrange
        dto = RegisterUserDTO(
            email="existente@test.com",
            password="password123",
            nombre="Usuario",
        )

        mock_repository.exists_by_email.return_value = True

        # Act & Assert
        with pytest.raises(EmailAlreadyExistsException) as exc_info:
            await use_case.execute(dto)

        assert "existente@test.com" in str(exc_info.value.message)
        mock_repository.exists_by_email.assert_called_once_with(dto.email)
        mock_repository.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_user_con_buffet_id(self, use_case, mock_repository, password_hasher):
        """Test registro de usuario cliente con buffet_id"""
        # Arrange
        dto = RegisterUserDTO(
            email="cliente@test.com",
            password="password123",
            nombre="Cliente Test",
            rol=RolEnum.CLIENTE,
            buffet_id=1,
        )

        password_hash = password_hasher.hash(dto.password)
        usuario_creado = Usuario.crear(
            email=dto.email,
            nombre=dto.nombre,
            password_hash=password_hash,
            rol=dto.rol,
            buffet_id=dto.buffet_id,
        )
        usuario_creado.id = 2

        mock_repository.exists_by_email.return_value = False
        mock_repository.add.return_value = usuario_creado

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.buffet_id == 1
        assert result.rol == RolEnum.CLIENTE.value

    @pytest.mark.asyncio
    async def test_register_user_admin_sin_buffet(self, use_case, mock_repository, password_hasher):
        """Test registro de admin sin buffet_id"""
        # Arrange
        dto = RegisterUserDTO(
            email="admin@test.com",
            password="password123",
            nombre="Admin Test",
            rol=RolEnum.ADMIN,
        )

        password_hash = password_hasher.hash(dto.password)
        usuario_creado = Usuario.crear(
            email=dto.email,
            nombre=dto.nombre,
            password_hash=password_hash,
            rol=dto.rol,
        )
        usuario_creado.id = 3

        mock_repository.exists_by_email.return_value = False
        mock_repository.add.return_value = usuario_creado

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.rol == RolEnum.ADMIN.value
        assert result.buffet_id is None
