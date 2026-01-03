"""
Tests para JWTService.

Verifica la creación y decodificación de tokens JWT.
"""

import pytest
from datetime import timedelta

from src.modules.usuarios.infrastructure.services.jwt_service import JWTService
from src.shared.domain.enums import RolEnum


class TestJWTService:
    """Tests para JWTService"""

    @pytest.fixture
    def jwt_service(self):
        """Instancia del servicio JWT"""
        return JWTService()

    def test_create_access_token(self, jwt_service):
        """Test creación de token de acceso"""
        token = jwt_service.create_access_token(
            user_id=1,
            email="test@test.com",
            rol=RolEnum.ADMIN,
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        # Los tokens JWT tienen 3 partes separadas por puntos
        assert len(token.split(".")) == 3

    def test_create_access_token_con_buffet_id(self, jwt_service):
        """Test creación de token con buffet_id"""
        token = jwt_service.create_access_token(
            user_id=2,
            email="cliente@test.com",
            rol=RolEnum.CLIENTE,
            buffet_id=1,
        )

        assert token is not None
        payload = jwt_service.decode_token(token)
        assert payload is not None
        assert payload["buffet_id"] == 1

    def test_decode_token_valido(self, jwt_service):
        """Test decodificación de token válido"""
        token = jwt_service.create_access_token(
            user_id=1,
            email="test@test.com",
            rol=RolEnum.ADMIN,
        )

        payload = jwt_service.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["email"] == "test@test.com"
        assert payload["rol"] == RolEnum.ADMIN.value
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_token_invalido(self, jwt_service):
        """Test decodificación de token inválido retorna None"""
        token_invalido = "token.invalido.malformado"

        payload = jwt_service.decode_token(token_invalido)

        assert payload is None

    def test_get_user_id_from_token(self, jwt_service):
        """Test extracción de user_id desde token"""
        token = jwt_service.create_access_token(
            user_id=123,
            email="test@test.com",
            rol=RolEnum.INVESTIGADOR,
        )

        user_id = jwt_service.get_user_id_from_token(token)

        assert user_id == 123

    def test_get_user_id_from_token_invalido(self, jwt_service):
        """Test extracción de user_id desde token inválido retorna None"""
        token_invalido = "token.invalido"

        user_id = jwt_service.get_user_id_from_token(token_invalido)

        assert user_id is None

    def test_get_rol_from_token(self, jwt_service):
        """Test extracción de rol desde token"""
        token = jwt_service.create_access_token(
            user_id=1,
            email="test@test.com",
            rol=RolEnum.CLIENTE,
        )

        rol = jwt_service.get_rol_from_token(token)

        assert rol == RolEnum.CLIENTE

    def test_get_rol_from_token_invalido(self, jwt_service):
        """Test extracción de rol desde token inválido retorna None"""
        token_invalido = "token.invalido"

        rol = jwt_service.get_rol_from_token(token_invalido)

        assert rol is None

    def test_is_token_expired_token_valido(self, jwt_service):
        """Test que token válido no está expirado"""
        token = jwt_service.create_access_token(
            user_id=1,
            email="test@test.com",
            rol=RolEnum.ADMIN,
        )

        assert jwt_service.is_token_expired(token) is False

    def test_is_token_expired_token_invalido(self, jwt_service):
        """Test que token inválido está marcado como expirado"""
        token_invalido = "token.invalido"

        assert jwt_service.is_token_expired(token_invalido) is True

    def test_create_token_con_expires_delta(self, jwt_service):
        """Test creación de token con tiempo de expiración personalizado"""
        expires_delta = timedelta(minutes=60)
        token = jwt_service.create_access_token(
            user_id=1,
            email="test@test.com",
            rol=RolEnum.ADMIN,
            expires_delta=expires_delta,
        )

        payload = jwt_service.decode_token(token)
        assert payload is not None
        # Verificar que el token tiene expiración (no verificamos el tiempo exacto)
