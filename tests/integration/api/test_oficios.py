"""
Tests de integración para endpoints de Oficios.

Verifica el CRUD completo de oficios y sus relaciones.
"""

import pytest
from fastapi import status


class TestOficiosEndpoints:
    """Tests para endpoints de oficios"""

    @pytest.mark.asyncio
    async def test_create_oficio_exitoso(self, test_client, auth_headers, test_buffet):
        """Test creación exitosa de oficio"""
        response = test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-001",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "ABCD12",
                    "marca": "Toyota",
                    "modelo": "Corolla",
                    "año": 2020,
                    "color": "Blanco",
                },
                "prioridad": "media",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["numero_oficio"] == "OF-2024-001"
        assert data["buffet_id"] == test_buffet.id
        assert "vehiculo" in data
        assert data["vehiculo"]["patente"] == "ABCD12"

    @pytest.mark.asyncio
    async def test_create_oficio_con_propietarios(self, test_client, auth_headers, test_buffet):
        """Test creación de oficio con propietarios"""
        response = test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-002",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "EFGH34",
                },
                "propietarios": [
                    {
                        "rut": "12345678-9",
                        "nombre_completo": "Juan Perez",
                        "tipo": "principal",
                    }
                ],
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["propietarios"]) == 1
        assert data["propietarios"][0]["rut"] == "12345678-9"

    @pytest.mark.asyncio
    async def test_get_oficio_by_id(self, test_client, auth_headers, test_buffet, db_session):
        """Test obtención de oficio por ID"""
        # Crear oficio primero
        create_response = test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-003",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "IJKL56",
                },
            },
        )
        oficio_id = create_response.json()["id"]

        # Obtener oficio
        response = test_client.get(
            f"/api/v1/oficios/{oficio_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == oficio_id
        assert data["numero_oficio"] == "OF-2024-003"

    @pytest.mark.asyncio
    async def test_list_oficios(self, test_client, auth_headers, test_buffet):
        """Test listado de oficios"""
        response = test_client.get(
            "/api/v1/oficios",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_add_propietario_to_oficio(
        self, test_client, auth_headers, test_buffet, db_session
    ):
        """Test agregar propietario a oficio existente"""
        # Crear oficio
        create_response = test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-004",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "MNOP78",
                },
            },
        )
        oficio_id = create_response.json()["id"]

        # Agregar propietario
        response = test_client.post(
            f"/api/v1/oficios/{oficio_id}/propietarios",
            headers=auth_headers,
            json={
                "rut": "98765432-1",
                "nombre_completo": "Maria Lopez",
                "tipo": "codeudor",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["rut"] == "98765432-1"
        assert data["nombre_completo"] == "Maria Lopez"

    @pytest.mark.asyncio
    async def test_add_direccion_to_oficio(
        self, test_client, auth_headers, test_buffet, db_session
    ):
        """Test agregar dirección a oficio existente"""
        # Crear oficio
        create_response = test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-005",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "QRST90",
                },
            },
        )
        oficio_id = create_response.json()["id"]

        # Agregar dirección
        response = test_client.post(
            f"/api/v1/oficios/{oficio_id}/direcciones",
            headers=auth_headers,
            json={
                "direccion": "Av. Providencia 1234",
                "comuna": "Providencia",
                "region": "Metropolitana",
                "tipo": "domicilio",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["direccion"] == "Av. Providencia 1234"
        assert data["comuna"] == "Providencia"
