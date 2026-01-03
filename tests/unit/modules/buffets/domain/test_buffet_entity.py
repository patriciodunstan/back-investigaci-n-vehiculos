"""
Tests unitarios para la entidad Buffet.

Prueba la lógica de dominio sin dependencias de infraestructura.
"""

import pytest

from src.modules.buffets.domain.entities import Buffet


class TestBuffetEntity:
    """Tests para la entidad Buffet."""

    def test_crear_buffet_exitoso(self):
        """Buffet se crea correctamente con datos válidos."""
        buffet = Buffet.crear(
            nombre="Buffet Test",
            rut="12345678-5",
            email_principal="buffet@test.com",
        )

        assert buffet.nombre == "Buffet Test"
        assert buffet.rut_str == "12345678-5"
        assert buffet.email_str == "buffet@test.com"
        assert buffet.activo is True
        assert buffet.token_tablero is not None
        assert len(buffet.token_tablero) > 0

    def test_crear_buffet_con_datos_completos(self):
        """Buffet se crea con todos los campos opcionales."""
        buffet = Buffet.crear(
            nombre="Buffet Completo",
            rut="98765432-1",
            email_principal="completo@test.com",
            telefono="+56912345678",
            contacto_nombre="Contacto Test",
        )

        assert buffet.telefono == "+56912345678"
        assert buffet.contacto_nombre == "Contacto Test"

    def test_buffet_normaliza_nombre(self):
        """Buffet normaliza espacios en el nombre."""
        buffet = Buffet.crear(
            nombre="  Buffet Test  ",
            rut="12345678-5",
            email_principal="test@test.com",
        )

        assert buffet.nombre == "Buffet Test"

    def test_desactivar_buffet(self):
        """Desactivar buffet cambia estado a inactivo."""
        buffet = Buffet.crear(
            nombre="Buffet Test",
            rut="12345678-5",
            email_principal="test@test.com",
        )

        buffet.desactivar()

        assert buffet.activo is False

    def test_activar_buffet(self):
        """Activar buffet cambia estado a activo."""
        buffet = Buffet.crear(
            nombre="Buffet Test",
            rut="12345678-5",
            email_principal="test@test.com",
        )
        buffet.desactivar()

        buffet.activar()

        assert buffet.activo is True

    def test_regenerar_token(self):
        """Regenerar token crea un nuevo token."""
        buffet = Buffet.crear(
            nombre="Buffet Test",
            rut="12345678-5",
            email_principal="test@test.com",
        )

        token_original = buffet.token_tablero
        nuevo_token = buffet.regenerar_token()

        assert nuevo_token != token_original
        assert buffet.token_tablero == nuevo_token

    def test_actualizar_buffet(self):
        """Actualizar buffet modifica campos."""
        buffet = Buffet.crear(
            nombre="Original",
            rut="12345678-5",
            email_principal="original@test.com",
        )

        buffet.actualizar(
            nombre="Actualizado",
            email_principal="actualizado@test.com",
            telefono="+56987654321",
            contacto_nombre="Nuevo Contacto",
        )

        assert buffet.nombre == "Actualizado"
        assert buffet.email_str == "actualizado@test.com"
        assert buffet.telefono == "+56987654321"
        assert buffet.contacto_nombre == "Nuevo Contacto"

    def test_actualizar_buffet_parcial(self):
        """Actualizar buffet solo con algunos campos."""
        buffet = Buffet.crear(
            nombre="Original",
            rut="12345678-5",
            email_principal="original@test.com",
            telefono="+56912345678",
        )

        buffet.actualizar(nombre="Actualizado")

        assert buffet.nombre == "Actualizado"
        assert buffet.email_str == "original@test.com"
        assert buffet.telefono == "+56912345678"

    def test_buffet_marca_actualizado_al_desactivar(self):
        """Desactivar buffet marca como actualizado."""
        buffet = Buffet.crear(
            nombre="Buffet Test",
            rut="12345678-5",
            email_principal="test@test.com",
        )

        original_updated_at = buffet.updated_at
        buffet.desactivar()

        assert buffet.updated_at > original_updated_at
