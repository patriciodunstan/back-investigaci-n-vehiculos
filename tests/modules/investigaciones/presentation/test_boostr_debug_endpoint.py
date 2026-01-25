"""
Tests para el cliente de Boostr.

Tests unitarios para el BoostrClient.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.shared.infrastructure.external_apis.boostr.client import BoostrClient


@pytest.mark.unit
class TestBoostrClient:
    """Tests para el cliente de Boostr."""

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

            assert "Accept" in headers
            assert "Content-Type" in headers
            assert "User-Agent" in headers
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test_key_123"

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

    def test_normalize_rut(self):
        """Test que normaliza RUTs correctamente."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="test",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()

            assert client._normalize_rut("12345678-9") == "12.345.678-9"
            assert client._normalize_rut("12.345.678-9") == "12.345.678-9"
            assert client._normalize_rut("123456789") == "12.345.678-9"

    def test_normalize_rut_with_k(self):
        """Test que normaliza RUTs con K correctamente."""
        with patch("src.shared.infrastructure.external_apis.boostr.client.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                BOOSTR_API_URL="https://api.boostr.cl",
                BOOSTR_API_KEY="test",
                BOOSTR_TIMEOUT=30,
            )

            client = BoostrClient()

            assert client._normalize_rut("12345678-k") == "12.345.678-K"
            assert client._normalize_rut("12345678k") == "12.345.678-K"
