"""
Tests unitarios para excepciones del módulo Oficios.
"""

import pytest

from src.modules.oficios.domain.exceptions import (
    OficioNotFoundException,
    NumeroOficioAlreadyExistsException,
    OficioYaFinalizadoException,
    VehiculoNotFoundException,
    PropietarioNotFoundException,
    DireccionNotFoundException,
)


class TestOficioExceptions:
    """Tests para excepciones del módulo Oficios."""

    def test_oficio_not_found_exception_con_id(self):
        """OficioNotFoundException con ID se crea correctamente."""
        exc = OficioNotFoundException(1)

        assert "1" in exc.message
        assert "ENTITY_NOT_FOUND" in exc.code or "OFICIO_NOT_FOUND" in exc.code

    def test_oficio_not_found_exception_con_numero(self):
        """OficioNotFoundException con número se crea correctamente."""
        exc = OficioNotFoundException("OF-2026-001")

        assert "OF-2026-001" in exc.message
        assert "ENTITY_NOT_FOUND" in exc.code or "OFICIO_NOT_FOUND" in exc.code

    def test_numero_oficio_already_exists_exception(self):
        """NumeroOficioAlreadyExistsException se crea correctamente."""
        exc = NumeroOficioAlreadyExistsException("OF-2026-001")

        assert "OF-2026-001" in exc.message
        assert "DUPLICATE_ENTITY" in exc.code

    def test_oficio_ya_finalizado_exception(self):
        """OficioYaFinalizadoException se crea correctamente."""
        exc = OficioYaFinalizadoException(1)

        assert "1" in exc.message
        assert exc.code == "OFICIO_FINALIZADO"

    def test_vehiculo_not_found_exception(self):
        """VehiculoNotFoundException se crea correctamente."""
        exc = VehiculoNotFoundException(1)

        assert "1" in exc.message
        assert "ENTITY_NOT_FOUND" in exc.code

    def test_propietario_not_found_exception(self):
        """PropietarioNotFoundException se crea correctamente."""
        exc = PropietarioNotFoundException(1)

        assert "1" in exc.message
        assert "ENTITY_NOT_FOUND" in exc.code

    def test_direccion_not_found_exception(self):
        """DireccionNotFoundException se crea correctamente."""
        exc = DireccionNotFoundException(1)

        assert "1" in exc.message
        assert "ENTITY_NOT_FOUND" in exc.code
