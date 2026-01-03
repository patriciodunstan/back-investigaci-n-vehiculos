"""
Tests de integración para endpoints de Notificaciones.

Verifica el envío y consulta de notificaciones.
"""

import pytest
from fastapi import status


class TestNotificacionesEndpoints:
    """Tests para endpoints de notificaciones"""

    @pytest.mark.asyncio
    async def test_create_notificacion(self, test_client, auth_headers, test_buffet, db_session):
        """Test crear notificación"""
        # Crear oficio
        create_response = test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-009",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "GHIJ78",
                },
            },
        )
        oficio_id = create_response.json()["id"]

        # Crear notificación
        response = test_client.post(
            f"/api/v1/notificaciones/oficios/{oficio_id}/notificaciones",
            headers=auth_headers,
            json={
                "tipo": "buffet",
                "destinatario": "cliente@test.com",
                "asunto": "Actualización de caso",
                "contenido": "Se ha encontrado el vehículo",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["tipo"] == "buffet"
        assert data["destinatario"] == "cliente@test.com"
        assert data["enviada"] is False  # Inicialmente no enviada

    @pytest.mark.asyncio
    async def test_list_notificaciones_oficio(
        self, test_client, auth_headers, test_buffet, db_session
    ):
        """Test listar notificaciones de un oficio"""
        # Crear oficio
        create_response = test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-010",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "KLMN90",
                },
            },
        )
        oficio_id = create_response.json()["id"]

        # Crear notificación
        test_client.post(
            f"/api/v1/notificaciones/oficios/{oficio_id}/notificaciones",
            headers=auth_headers,
            json={
                "tipo": "buffet",
                "destinatario": "cliente@test.com",
                "asunto": "Test",
            },
        )

        # Listar notificaciones
        response = test_client.get(
            f"/api/v1/notificaciones/oficios/{oficio_id}/notificaciones",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert data["oficio_id"] == oficio_id
        assert len(data["items"]) > 0
