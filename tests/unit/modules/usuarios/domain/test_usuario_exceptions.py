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

        assert "test@example.com" in exc.message
        assert exc.code == "DUPLICATE_ENTITY"

    def test_invalid_credentials_exception(self):
        """InvalidCredentialsException se crea correctamente."""
        exc = InvalidCredentialsException()

        assert "invalidas" in exc.message.lower() or "invalid" in exc.message.lower()
        assert exc.code == "INVALID_CREDENTIALS"

    def test_inactive_user_exception(self):
        """InactiveUserException se crea correctamente."""
        exc = InactiveUserException("test@example.com")

        assert "test@example.com" in exc.message
        assert exc.code == "INACTIVE_USER"

    def test_invalid_token_exception(self):
        """InvalidTokenException se crea correctamente."""
        exc = InvalidTokenException()

        assert "token" in exc.message.lower()
        assert exc.code == "INVALID_TOKEN"

    def test_usuario_not_found_exception(self):
        """UsuarioNotFoundException se crea correctamente."""
        exc = UsuarioNotFoundException("test@example.com")

        assert "test@example.com" in exc.message
        assert "USER_NOT_FOUND" in exc.code or "ENTITY_NOT_FOUND" in exc.code
