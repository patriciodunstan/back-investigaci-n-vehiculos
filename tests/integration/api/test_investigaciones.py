"""
Tests de integración para endpoints de Investigaciones.

Verifica el timeline y actividades de investigación.
"""

import pytest
from fastapi import status


class TestInvestigacionesEndpoints:
    """Tests para endpoints de investigaciones"""

    @pytest.mark.asyncio
    async def test_add_actividad_to_oficio(
        self, test_client, auth_headers, test_buffet, investigador_user, db_session
    ):
        """Test agregar actividad a oficio"""
        # Crear oficio
        create_response = await test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-006",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "UVWX12",
                },
            },
        )
        await db_session.commit()
        oficio_id = create_response.json()["id"]

        # Agregar actividad
        response = await test_client.post(
            f"/api/v1/investigaciones/oficios/{oficio_id}/actividades",
            headers=auth_headers,
            json={
                "tipo_actividad": "nota",
                "descripcion": "Visita realizada a dirección registrada",
                "resultado": "No se encontró el vehículo",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["tipo_actividad"] == "nota"
        assert data["descripcion"] == "Visita realizada a dirección registrada"

    @pytest.mark.asyncio
    async def test_get_timeline_oficio(self, test_client, auth_headers, test_buffet, db_session):
        """Test obtener timeline de oficio"""
        # Crear oficio
        create_response = await test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-007",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "YZAB34",
                },
            },
        )
        await db_session.commit()
        oficio_id = create_response.json()["id"]

        # Agregar actividad
        await test_client.post(
            f"/api/v1/investigaciones/oficios/{oficio_id}/actividades",
            headers=auth_headers,
            json={
                "tipo_actividad": "nota",
                "descripcion": "Actividad de prueba",
            },
        )

        # Obtener timeline
        response = await test_client.get(
            f"/api/v1/investigaciones/oficios/{oficio_id}/timeline",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert data["oficio_id"] == oficio_id
        assert len(data["items"]) > 0

    @pytest.mark.asyncio
    async def test_add_avistamiento(self, test_client, auth_headers, test_buffet, db_session):
        """Test agregar avistamiento"""
        # Crear oficio
        create_response = await test_client.post(
            "/api/v1/oficios",
            headers=auth_headers,
            json={
                "numero_oficio": "OF-2024-008",
                "buffet_id": test_buffet.id,
                "vehiculo": {
                    "patente": "CDEF56",
                },
            },
        )
        await db_session.commit()
        oficio_id = create_response.json()["id"]

        # Agregar avistamiento
        response = await test_client.post(
            f"/api/v1/investigaciones/oficios/{oficio_id}/avistamientos",
            headers=auth_headers,
            json={
                "fuente": "terreno",
                "ubicacion": "Av. Providencia 1234",
                "latitud": -33.4269,
                "longitud": -70.6150,
                "notas": "Vehículo estacionado",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["fuente"] == "terreno"
        assert data["ubicacion"] == "Av. Providencia 1234"
