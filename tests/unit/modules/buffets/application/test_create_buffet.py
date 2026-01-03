"""
Tests para CreateBuffetUseCase.

Verifica la creación de buffets con diferentes escenarios.
"""

import pytest
from unittest.mock import AsyncMock

from src.modules.buffets.application.use_cases.create_buffet import CreateBuffetUseCase
from src.modules.buffets.application.dtos import CreateBuffetDTO
from src.modules.buffets.domain.entities import Buffet
from src.modules.buffets.domain.exceptions import RutAlreadyExistsException


class TestCreateBuffetUseCase:
    """Tests para CreateBuffetUseCase"""

    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio de buffets"""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        """Instancia del use case con mock"""
        return CreateBuffetUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_create_buffet_exitoso(self, use_case, mock_repository):
        """Test creación exitosa de buffet"""
        # Arrange
        dto = CreateBuffetDTO(
            nombre="Buffet Test",
            rut="12345678-5",
            email_principal="buffet@test.com",
            telefono="+56912345678",
            contacto_nombre="Contacto Test",
        )

        buffet_creado = Buffet.crear(
            nombre=dto.nombre,
            rut=dto.rut,
            email_principal=dto.email_principal,
            telefono=dto.telefono,
            contacto_nombre=dto.contacto_nombre,
        )
        buffet_creado.id = 1

        mock_repository.exists_by_rut.return_value = False
        mock_repository.add.return_value = buffet_creado

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.id == 1
        assert result.nombre == dto.nombre
        assert result.rut == dto.rut
        assert result.email_principal == dto.email_principal
        mock_repository.exists_by_rut.assert_called_once_with(dto.rut)
        mock_repository.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_buffet_rut_duplicado(self, use_case, mock_repository):
        """Test que lanza excepción cuando el RUT ya existe"""
        # Arrange
        dto = CreateBuffetDTO(
            nombre="Buffet Duplicado",
            rut="12345678-5",
            email_principal="duplicado@test.com",
        )

        mock_repository.exists_by_rut.return_value = True

        # Act & Assert
        with pytest.raises(RutAlreadyExistsException) as exc_info:
            await use_case.execute(dto)

        assert "12345678-5" in str(exc_info.value.message)
        mock_repository.exists_by_rut.assert_called_once_with(dto.rut)
        mock_repository.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_buffet_sin_telefono(self, use_case, mock_repository):
        """Test creación de buffet sin teléfono opcional"""
        # Arrange
        dto = CreateBuffetDTO(
            nombre="Buffet Sin Telefono",
            rut="87654321-K",
            email_principal="sintelefono@test.com",
        )

        buffet_creado = Buffet.crear(
            nombre=dto.nombre,
            rut=dto.rut,
            email_principal=dto.email_principal,
        )
        buffet_creado.id = 2

        mock_repository.exists_by_rut.return_value = False
        mock_repository.add.return_value = buffet_creado

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.id == 2
        assert result.telefono is None
