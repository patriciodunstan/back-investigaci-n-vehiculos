"""
Tests para LoginUserUseCase.

Verifica el login de usuarios con diferentes escenarios.
"""

import pytest
from unittest.mock import AsyncMock

from src.modules.usuarios.application.use_cases.login_user import LoginUserUseCase
from src.modules.usuarios.application.dtos import LoginDTO
from src.modules.usuarios.domain.entities import Usuario
from src.modules.usuarios.domain.exceptions import (
    InvalidCredentialsException,
    InactiveUserException,
)
from src.shared.domain.enums import RolEnum


class TestLoginUserUseCase:
    """Tests para LoginUserUseCase"""

    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio de usuarios"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        """Instancia del use case con mock"""
        return LoginUserUseCase(mock_repository)

    @pytest.fixture
    def usuario_activo(self, password_hasher):
        """Usuario activo para tests"""
        password_hash = password_hasher.hash("password123")
        usuario = Usuario.crear(
            email="test@test.com",
            nombre="Test User",
            password_hash=password_hash,
            rol=RolEnum.CLIENTE,
            activo=True,
        )
        object.__setattr__(usuario, "id", 1)
        return usuario

    @pytest.mark.asyncio
    async def test_login_exitoso(self, use_case, mock_repository, usuario_activo):
        """Test login exitoso con credenciales válidas"""
        # Arrange
        dto = LoginDTO(email="test@test.com", password="password123")
        mock_repository.get_by_email.return_value = usuario_activo

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.access_token is not None
        assert len(result.access_token) > 0
        assert result.token_type == "bearer"
        assert result.expires_in > 0
        mock_repository.get_by_email.assert_called_once_with(dto.email)

    @pytest.mark.asyncio
    async def test_login_usuario_no_existe(self, use_case, mock_repository):
        """Test que lanza excepción cuando el usuario no existe"""
        # Arrange
        dto = LoginDTO(email="noexiste@test.com", password="password123")
        mock_repository.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(InvalidCredentialsException):
            await use_case.execute(dto)

        mock_repository.get_by_email.assert_called_once_with(dto.email)

    @pytest.mark.asyncio
    async def test_login_password_incorrecta(self, use_case, mock_repository, usuario_activo):
        """Test que lanza excepción cuando la contraseña es incorrecta"""
        # Arrange
        dto = LoginDTO(email="test@test.com", password="password_incorrecta")
        mock_repository.get_by_email.return_value = usuario_activo

        # Act & Assert
        with pytest.raises(InvalidCredentialsException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_login_usuario_inactivo(self, use_case, mock_repository, password_hasher):
        """Test que lanza excepción cuando el usuario está inactivo"""
        # Arrange
        password_hash = password_hasher.hash("password123")
        usuario_inactivo = Usuario.crear(
            email="inactivo@test.com",
            nombre="Usuario Inactivo",
            password_hash=password_hash,
            rol=RolEnum.CLIENTE,
            activo=False,
        )
        object.__setattr__(usuario_inactivo, "id", 2)

        dto = LoginDTO(email="inactivo@test.com", password="password123")
        mock_repository.get_by_email.return_value = usuario_inactivo

        # Act & Assert
        with pytest.raises(InactiveUserException) as exc_info:
            await use_case.execute(dto)

        assert "inactivo@test.com" in str(exc_info.value.message)
