"""
Tests unitarios para excepciones del módulo Usuarios.
"""

import pytest

from src.modules.usuarios.domain.exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    InactiveUserException,
    InvalidTokenException,
    UsuarioNotFoundException,
)


class TestUsuarioExceptions:
    """Tests para excepciones del módulo Usuarios."""

    def test_email_already_exists_exception(self):
        """EmailAlreadyExistsException se crea correctamente."""
        exc = EmailAlreadyExistsException("test@example.com")

        assert exc.message == "El email 'test@example.com' ya está registrado."
        assert exc.code == "EMAIL_ALREADY_EXISTS"
        assert str(exc) == "El email 'test@example.com' ya está registrado."

    def test_invalid_credentials_exception(self):
        """InvalidCredentialsException se crea correctamente."""
        exc = InvalidCredentialsException()

        assert exc.message == "Credenciales de acceso inválidas."
        assert exc.code == "INVALID_CREDENTIALS"

    def test_inactive_user_exception(self):
        """InactiveUserException se crea correctamente."""
        exc = InactiveUserException()

        assert exc.message == "El usuario está inactivo."
        assert exc.code == "INACTIVE_USER"

    def test_invalid_token_exception(self):
        """InvalidTokenException se crea correctamente."""
        exc = InvalidTokenException()

        assert exc.message == "Token inválido o expirado."
        assert exc.code == "INVALID_TOKEN"

    def test_usuario_not_found_exception(self):
        """UsuarioNotFoundException se crea correctamente."""
        exc = UsuarioNotFoundException("test@example.com")

        assert exc.message == "Usuario 'test@example.com' no encontrado."
        assert exc.code == "USUARIO_NOT_FOUND"
