"""
Tests de integración para endpoints de autenticación.

Verifica el flujo completo de registro, login y obtención de usuario actual.
"""

import pytest
from fastapi import status

from src.shared.domain.enums import RolEnum


class TestAuthEndpoints:
    """Tests para endpoints de autenticación"""

    @pytest.mark.asyncio
    async def test_register_user_exitoso(self, test_client, db_session):
        """Test registro exitoso de usuario"""
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "nuevo@test.com",
                "password": "password123",
                "nombre": "Usuario Nuevo",
                "rol": "cliente",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "nuevo@test.com"
        assert data["nombre"] == "Usuario Nuevo"
        assert data["rol"] == "cliente"
        assert "id" in data
        assert data["activo"] is True

    @pytest.mark.asyncio
    async def test_register_user_email_duplicado(self, test_client, admin_user):
        """Test que registro con email duplicado retorna error"""
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_user.email_str,
                "password": "password123",
                "nombre": "Usuario Duplicado",
            },
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_login_exitoso(self, test_client, admin_user):
        """Test login exitoso"""
        response = await test_client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_user.email_str,
                "password": "admin123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_json_exitoso(self, test_client, admin_user):
        """Test login usando JSON en lugar de form-data"""
        response = await test_client.post(
            "/api/v1/auth/login/json",
            json={
                "email": admin_user.email_str,
                "password": "admin123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_credenciales_incorrectas(self, test_client):
        """Test login con credenciales incorrectas"""
        response = await test_client.post(
            "/api/v1/auth/login",
            data={
                "username": "noexiste@test.com",
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_exitoso(self, test_client, auth_headers):
        """Test obtención del usuario actual con token válido"""
        response = await test_client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "nombre" in data
        assert "rol" in data

    @pytest.mark.asyncio
    async def test_get_current_user_sin_token(self, test_client):
        """Test que obtener usuario sin token retorna error"""
        response = await test_client.get("/api/v1/auth/me")

        # Puede ser 401 o 403 dependiendo de la configuración
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_get_current_user_token_invalido(self, test_client):
        """Test que obtener usuario con token inválido retorna error"""
        response = await test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer token_invalido"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
