"""
Tests unitarios para excepciones del módulo Buffets.
"""

import pytest

from src.modules.buffets.domain.exceptions import (
    BuffetNotFoundException,
    RutAlreadyExistsException,
)


class TestBuffetExceptions:
    """Tests para excepciones del módulo Buffets."""

    def test_buffet_not_found_exception(self):
        """BuffetNotFoundException se crea correctamente."""
        exc = BuffetNotFoundException(1)

        assert exc.message == "Buffet con ID 1 no encontrado"
        assert exc.code == "BUFFET_NOT_FOUND"

    def test_rut_already_exists_exception(self):
        """RutAlreadyExistsException se crea correctamente."""
        exc = RutAlreadyExistsException("12345678-5")

        assert exc.message == "El RUT '12345678-5' ya está registrado."
        assert exc.code == "RUT_ALREADY_EXISTS"
