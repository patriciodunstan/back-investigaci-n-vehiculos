"""
Tests para GetCurrentUserUseCase.

Verifica la obtención del usuario actual desde token JWT.
"""

import pytest
from unittest.mock import AsyncMock

from src.modules.usuarios.application.use_cases.get_current_user import GetCurrentUserUseCase
from src.modules.usuarios.domain.entities import Usuario
from src.modules.usuarios.domain.exceptions import (
    InvalidTokenException,
    UsuarioNotFoundException,
    InactiveUserException,
)
from src.shared.domain.enums import RolEnum


class TestGetCurrentUserUseCase:
    """Tests para GetCurrentUserUseCase"""

    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio de usuarios"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        """Instancia del use case con mock"""
        return GetCurrentUserUseCase(mock_repository)

    @pytest.fixture
    def usuario_activo(self):
        """Usuario activo para tests"""
        usuario = Usuario.crear(
            email="test@test.com",
            nombre="Test User",
            password_hash="hashed",
            rol=RolEnum.ADMIN,
            activo=True,
        )
        usuario.id = 1
        return usuario

    @pytest.mark.asyncio
    async def test_get_current_user_exitoso(self, use_case, mock_repository, usuario_activo):
        """Test obtención exitosa del usuario actual"""
        # Arrange - crear token real
        from src.modules.usuarios.infrastructure.services import jwt_service

        token = jwt_service.create_access_token(
            user_id=usuario_activo.id,
            email=usuario_activo.email_str,
            rol=usuario_activo.rol,
            buffet_id=usuario_activo.buffet_id,
        )

        mock_repository.get_by_id.return_value = usuario_activo

        # Act
        result = await use_case.execute(token)

        # Assert
        assert result.id == 1
        assert result.email == usuario_activo.email_str
        assert result.rol == usuario_activo.rol.value
        mock_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_current_user_token_invalido(self, use_case, mock_repository):
        """Test que lanza excepción cuando el token es inválido"""
        # Arrange
        token = "invalid_token.invalid_token.invalid_token"

        # Act & Assert
        with pytest.raises(InvalidTokenException):
            await use_case.execute(token)

        mock_repository.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_user_no_encontrado(self, use_case, mock_repository):
        """Test que lanza excepción cuando el usuario no existe"""
        # Arrange - crear token con user_id que no existe
        from src.modules.usuarios.infrastructure.services import jwt_service

        token = jwt_service.create_access_token(
            user_id=999,
            email="noexiste@test.com",
            rol=RolEnum.CLIENTE,
        )

        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UsuarioNotFoundException):
            await use_case.execute(token)

    @pytest.mark.asyncio
    async def test_get_current_user_inactivo(self, use_case, mock_repository):
        """Test que lanza excepción cuando el usuario está inactivo"""
        # Arrange
        usuario_inactivo = Usuario.crear(
            email="inactivo@test.com",
            nombre="Inactivo",
            password_hash="hashed",
            rol=RolEnum.CLIENTE,
            activo=False,
        )
        usuario_inactivo.id = 2

        from src.modules.usuarios.infrastructure.services import jwt_service

        token = jwt_service.create_access_token(
            user_id=usuario_inactivo.id,
            email=usuario_inactivo.email_str,
            rol=usuario_inactivo.rol,
        )

        mock_repository.get_by_id.return_value = usuario_inactivo

        # Act & Assert
        with pytest.raises(InactiveUserException):
            await use_case.execute(token)
