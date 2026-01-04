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

        assert "1" in exc.message
        assert "ENTITY_NOT_FOUND" in exc.code or "BUFFET_NOT_FOUND" in exc.code

    def test_rut_already_exists_exception(self):
        """RutAlreadyExistsException se crea correctamente."""
        exc = RutAlreadyExistsException("12345678-5")

        assert "12345678-5" in exc.message
        assert "DUPLICATE_ENTITY" in exc.code or "RUT_ALREADY_EXISTS" in exc.code
