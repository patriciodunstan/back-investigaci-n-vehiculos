"""
Tests para mejoras en el cliente de Boostr.

Tests unitarios para las mejoras de logging y headers del BoostrClient.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.shared.infrastructure.external_apis.boostr.client import BoostrClient


@pytest.mark.unit
class TestBoostrClientImprovements:
    """Tests para las mejoras del cliente de Boostr."""

    def test_client_initialization_with_api_key(self):
        """Test que el cliente se inicializa correctamente con API key."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="test_api_key_1234",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()

            assert client.api_key == "test_api_key_1234"
            assert client.base_url == "https://api.boostr.cl"
            assert client.timeout == 30

    def test_client_initialization_without_api_key_logs_warning(self, caplog):
        """Test que el cliente loguea warning cuando no hay API key."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()

            assert client.api_key == ""
            assert "SIN API KEY" in caplog.text
            assert "NO CONFIGURADA" in caplog.text

    def test_get_headers_with_api_key_includes_bearer(self):
        """Test que los headers incluyen Authorization Bearer con API key."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="test_key_123",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()
            headers = client._get_headers()

            # Verificar que tiene todos los headers necesarios
            assert "Accept" in headers
            assert "Content-Type" in headers
            assert "User-Agent" in headers
            assert "Accept-Language" in headers
            assert "Accept-Encoding" in headers
            assert "Cache-Control" in headers
            assert "Pragma" in headers

            # Verificar autenticación
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test_key_123"
            assert "x-api-key" in headers
            assert headers["x-api-key"] == "test_key_123"

            # Verificar valores de headers para evitar bloqueos de Cloudflare
            assert "Mozilla" in headers["User-Agent"]
            assert headers["Accept"] == "application/json"

    def test_get_headers_with_bearer_prefix_doesnt_duplicate(self):
        """Test que no duplica el prefijo Bearer si ya lo tiene."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="Bearer already_has_prefix",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()
            headers = client._get_headers()

            assert headers["Authorization"] == "Bearer already_has_prefix"
            assert not headers["Authorization"].startswith("Bearer Bearer")

    def test_get_headers_without_api_key_logs_error(self, caplog):
        """Test que loguea error cuando intenta hacer request sin API key."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()
            headers = client._get_headers()

            assert "sin API key" in caplog.text.lower()
            assert "Authorization" not in headers or headers.get("Authorization") == "Bearer "

    def test_normalize_patente(self):
        """Test que normaliza patentes correctamente."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="test",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()

            # Normalización de patentes
            assert client._normalize_patente("  abc-123  ") == "ABC123"
            assert client._normalize_patente("xyz 456") == "XYZ456"
            assert client._normalize_patente("ABCD12") == "ABCD12"

    def test_normalize_rut(self):
        """Test que normaliza RUTs correctamente."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="test",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()

            # Normalización de RUTs
            assert client._normalize_rut("12345678-9") == "12.345.678-9"
            assert client._normalize_rut("12.345.678-9") == "12.345.678-9"
            assert client._normalize_rut("123456789") == "12.345.678-9"
