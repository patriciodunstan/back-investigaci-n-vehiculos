"""
Tests de integración para endpoints de Buffets.

Verifica el CRUD completo de buffets.
"""

import pytest
from fastapi import status


class TestBuffetsEndpoints:
    """Tests para endpoints de buffets"""

    @pytest.mark.asyncio
    async def test_create_buffet_exitoso(self, test_client, auth_headers):
        """Test creación exitosa de buffet"""
        response = await test_client.post(
            "/api/v1/buffets",
            headers=auth_headers,
            json={
                "nombre": "Buffet Test",
                "rut": "12345678-5",
                "email_principal": "buffet@test.com",
                "telefono": "+56912345678",
                "contacto_nombre": "Contacto Test",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == "Buffet Test"
        # RUT puede estar formateado con puntos
        assert "12345678" in data["rut"].replace(".", "")
        assert data["email_principal"] == "buffet@test.com"
        assert "id" in data
        assert "token_tablero" in data

    @pytest.mark.asyncio
    async def test_create_buffet_rut_duplicado(self, test_client, auth_headers, test_buffet):
        """Test que creación con RUT duplicado retorna error"""
        response = await test_client.post(
            "/api/v1/buffets",
            headers=auth_headers,
            json={
                "nombre": "Buffet Duplicado",
                "rut": test_buffet.rut_str,
                "email_principal": "duplicado@test.com",
            },
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_get_buffet_by_id(self, test_client, auth_headers, test_buffet):
        """Test obtención de buffet por ID"""
        response = await test_client.get(
            f"/api/v1/buffets/{test_buffet.id}",
            headers=auth_headers,
        )

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)
        data = response.json()
        assert data["id"] == test_buffet.id
        assert data["nombre"] == test_buffet.nombre

    @pytest.mark.asyncio
    async def test_get_buffet_no_existe(self, test_client, auth_headers):
        """Test que obtener buffet inexistente retorna error"""
        response = await test_client.get(
            "/api/v1/buffets/99999",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_list_buffets(self, test_client, auth_headers, test_buffet):
        """Test listado de buffets"""
        response = await test_client.get(
            "/api/v1/buffets",
            headers=auth_headers,
        )

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0

    @pytest.mark.asyncio
    async def test_update_buffet(self, test_client, auth_headers, test_buffet):
        """Test actualización de buffet"""
        response = await test_client.put(
            f"/api/v1/buffets/{test_buffet.id}",
            headers=auth_headers,
            json={
                "nombre": "Buffet Actualizado",
                "telefono": "+56987654321",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Buffet Actualizado"
        assert data["telefono"] == "+56987654321"

    @pytest.mark.asyncio
    async def test_delete_buffet(self, test_client, auth_headers, test_buffet):
        """Test eliminación (soft delete) de buffet"""
        response = await test_client.delete(
            f"/api/v1/buffets/{test_buffet.id}",
            headers=auth_headers,
        )

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)
