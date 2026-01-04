"""
Tests unitarios para la entidad Usuario.

Prueba la lógica de dominio sin dependencias de infraestructura.
"""

import pytest
import time
from datetime import datetime

from src.modules.usuarios.domain.entities import Usuario
from src.shared.domain.enums import RolEnum
from src.shared.domain.value_objects import Email


class TestUsuarioEntity:
    """Tests para la entidad Usuario."""

    def test_crear_usuario_exitoso(self):
        """Usuario se crea correctamente con datos válidos."""
        usuario = Usuario.crear(
            email="test@example.com",
            nombre="Test User",
            password_hash="hashed_password",
            rol=RolEnum.CLIENTE,
        )

        assert usuario.email.valor == "test@example.com"
        assert usuario.nombre == "Test User"
        assert usuario.password_hash == "hashed_password"
        assert usuario.rol == RolEnum.CLIENTE
        assert usuario.activo is True
        assert usuario.buffet_id is None

    def test_crear_usuario_admin(self):
        """Usuario admin se crea correctamente."""
        usuario = Usuario.crear(
            email="admin@test.com",
            nombre="Admin",
            password_hash="hash",
            rol=RolEnum.ADMIN,
        )

        assert usuario.rol == RolEnum.ADMIN
        assert usuario.buffet_id is None
        assert usuario.es_admin is True
        assert usuario.es_investigador is False
        assert usuario.es_cliente is False

    def test_crear_usuario_investigador(self):
        """Usuario investigador se crea correctamente."""
        usuario = Usuario.crear(
            email="investigador@test.com",
            nombre="Investigador",
            password_hash="hash",
            rol=RolEnum.INVESTIGADOR,
        )

        assert usuario.rol == RolEnum.INVESTIGADOR
        assert usuario.buffet_id is None
        assert usuario.es_investigador is True

    def test_crear_usuario_cliente_con_buffet(self):
        """Usuario cliente puede tener buffet_id."""
        usuario = Usuario.crear(
            email="cliente@test.com",
            nombre="Cliente",
            password_hash="hash",
            rol=RolEnum.CLIENTE,
            buffet_id=1,
        )

        assert usuario.rol == RolEnum.CLIENTE
        assert usuario.buffet_id == 1
        assert usuario.es_cliente is True

    def test_usuario_admin_no_puede_tener_buffet(self):
        """Usuario admin no puede tener buffet_id."""
        with pytest.raises(ValueError, match="no debe tener buffet_id"):
            Usuario.crear(
                email="admin@test.com",
                nombre="Admin",
                password_hash="hash",
                rol=RolEnum.ADMIN,
                buffet_id=1,
            )

    def test_usuario_investigador_no_puede_tener_buffet(self):
        """Usuario investigador no puede tener buffet_id."""
        with pytest.raises(ValueError, match="no debe tener buffet_id"):
            Usuario.crear(
                email="investigador@test.com",
                nombre="Investigador",
                password_hash="hash",
                rol=RolEnum.INVESTIGADOR,
                buffet_id=1,
            )

    def test_actualizar_perfil(self):
        """Actualizar perfil modifica nombre y avatar."""
        usuario = Usuario.crear(
            email="test@example.com",
            nombre="Original",
            password_hash="hash",
        )

        usuario.actualizar_perfil(nombre="Nuevo Nombre", avatar_url="http://example.com/avatar.jpg")

        assert usuario.nombre == "Nuevo Nombre"
        assert usuario.avatar_url == "http://example.com/avatar.jpg"

    def test_actualizar_perfil_solo_nombre(self):
        """Actualizar perfil solo con nombre."""
        usuario = Usuario.crear(
            email="test@example.com",
            nombre="Original",
            password_hash="hash",
        )

        usuario.actualizar_perfil(nombre="Nuevo Nombre", avatar_url=None)

        assert usuario.nombre == "Nuevo Nombre"
        assert usuario.avatar_url is None

    def test_cambiar_contrasena(self):
        """Cambiar contraseña actualiza el hash."""
        usuario = Usuario.crear(
            email="test@example.com",
            nombre="Test",
            password_hash="old_hash",
        )

        usuario.cambiar_contrasena("new_hash")

        assert usuario.password_hash == "new_hash"

    def test_activar_usuario(self):
        """Activar usuario cambia estado a activo."""
        usuario = Usuario.crear(
            email="test@example.com",
            nombre="Test",
            password_hash="hash",
            activo=False,
        )

        usuario.activar()

        assert usuario.activo is True

    def test_desactivar_usuario(self):
        """Desactivar usuario cambia estado a inactivo."""
        usuario = Usuario.crear(
            email="test@example.com",
            nombre="Test",
            password_hash="hash",
            activo=True,
        )

        usuario.desactivar()

        assert usuario.activo is False

    def test_email_str_property(self):
        """Property email_str retorna email como string."""
        usuario = Usuario.crear(
            email="test@example.com",
            nombre="Test",
            password_hash="hash",
        )

        assert usuario.email_str == "test@example.com"

    def test_usuario_marca_actualizado_al_cambiar_perfil(self):
        """Actualizar perfil marca el usuario como actualizado."""
        usuario = Usuario.crear(
            email="test@example.com",
            nombre="Test",
            password_hash="hash",
        )

        original_updated_at = usuario.updated_at
        time.sleep(0.01)  # Pequeña pausa para asegurar diferencia de tiempo
        usuario.actualizar_perfil(nombre="Nuevo")

        assert usuario.updated_at >= original_updated_at
