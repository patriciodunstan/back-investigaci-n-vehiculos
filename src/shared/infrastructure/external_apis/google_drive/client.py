"""
Cliente HTTP para la API de Google Drive.

Implementa la integración con Google Drive API usando Service Account
para autenticación y acceso a archivos y carpetas.

Documentación: https://developers.google.com/drive/api
"""

import json
import logging
from typing import Optional, List, BinaryIO
from datetime import datetime
from io import BytesIO

import httpx
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from src.core.config import get_settings
from .schemas import DriveFileMetadata, DriveFileListResponse
from .exceptions import (
    GoogleDriveAPIError,
    GoogleDriveAuthenticationError,
    GoogleDriveNotFoundError,
    GoogleDrivePermissionError,
    GoogleDriveQuotaExceededError,
    GoogleDriveTimeoutError,
)


logger = logging.getLogger(__name__)


class GoogleDriveClient:
    """
    Cliente para la API de Google Drive usando Service Account.

    Proporciona métodos para:
    - Descargar archivos desde Google Drive
    - Listar archivos en una carpeta
    - Obtener metadatos de archivos

    Attributes:
        credentials: Credenciales de Service Account
        timeout: Timeout en segundos para las requests

    Example:
        >>> client = GoogleDriveClient()
        >>> file_metadata = await client.get_file_metadata("file_id")
        >>> file_content = await client.download_file("file_id")
    """

    BASE_URL = "https://www.googleapis.com/drive/v3"

    def __init__(
        self,
        service_account_json: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        Inicializa el cliente de Google Drive.

        Args:
            service_account_json: JSON de Service Account como string o path a archivo
            timeout: Timeout en segundos (default: 30)
        """
        settings = get_settings()
        self.timeout = timeout or 30

        # Cargar credenciales de Service Account
        sa_json = service_account_json or settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON
        if not sa_json:
            raise GoogleDriveAuthenticationError("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON no configurado")

        try:
            # Intentar parsear como JSON string primero
            if sa_json.strip().startswith("{"):
                sa_info = json.loads(sa_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    sa_info,
                    scopes=["https://www.googleapis.com/auth/drive.readonly"],
                )
            else:
                # Asumir que es un path a archivo JSON
                self.credentials = service_account.Credentials.from_service_account_file(
                    sa_json,
                    scopes=["https://www.googleapis.com/auth/drive.readonly"],
                )

            # Refrescar token si es necesario
            if not self.credentials.valid:
                self.credentials.refresh(Request())

            logger.info("GoogleDriveClient inicializado con Service Account")

        except json.JSONDecodeError as e:
            raise GoogleDriveAuthenticationError(f"JSON de Service Account inválido: {str(e)}")
        except Exception as e:
            raise GoogleDriveAuthenticationError(f"Error cargando credenciales: {str(e)}")

    # =========================================================================
    # MÉTODOS PRIVADOS
    # =========================================================================

    def _get_access_token(self) -> str:
        """
        Obtiene un token de acceso válido.

        Returns:
            Token de acceso como string
        """
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return self.credentials.token

    def _get_headers(self) -> dict:
        """Retorna los headers necesarios para las requests."""
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Accept": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict:
        """
        Realiza una request a la API de Google Drive.

        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API (sin URL base)
            params: Parámetros de query string
            headers: Headers adicionales (se combinan con headers por defecto)

        Returns:
            Dict con la respuesta JSON

        Raises:
            GoogleDriveAPIError: En caso de error
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        logger.debug(f"Google Drive request: {method} {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                )

                # Manejar errores HTTP
                if response.status_code == 401:
                    raise GoogleDriveAuthenticationError("Credenciales inválidas o expiradas")
                elif response.status_code == 403:
                    raise GoogleDrivePermissionError(
                        "Permisos insuficientes. Verifique que el Service Account tenga acceso a la carpeta."
                    )
                elif response.status_code == 404:
                    raise GoogleDriveNotFoundError(f"Recurso no encontrado: {endpoint}")
                elif response.status_code == 429:
                    raise GoogleDriveQuotaExceededError()
                elif response.status_code >= 500:
                    raise GoogleDriveAPIError(
                        f"Error del servidor de Google Drive: {response.status_code}",
                        status_code=response.status_code,
                    )
                elif not response.is_success:
                    error_data = (
                        response.json()
                        if response.headers.get("content-type", "").startswith("application/json")
                        else {}
                    )
                    error_message = error_data.get("error", {}).get(
                        "message", f"Error HTTP {response.status_code}"
                    )
                    raise GoogleDriveAPIError(
                        error_message,
                        status_code=response.status_code,
                    )

                return response.json()

        except httpx.TimeoutException:
            raise GoogleDriveTimeoutError()
        except httpx.RequestError as e:
            raise GoogleDriveAPIError(f"Error de conexión: {str(e)}")

    async def _download_request(
        self,
        file_id: str,
    ) -> bytes:
        """
        Descarga un archivo desde Google Drive.

        Args:
            file_id: ID del archivo a descargar

        Returns:
            Bytes del archivo

        Raises:
            GoogleDriveAPIError: En caso de error
        """
        url = f"{self.BASE_URL}/files/{file_id}"
        params = {"alt": "media"}
        request_headers = self._get_headers()

        logger.debug(f"Google Drive download: {file_id}")

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout * 2
            ) as client:  # Más tiempo para descargas
                response = await client.get(
                    url=url,
                    headers=request_headers,
                    params=params,
                )

                # Manejar errores HTTP (igual que _request)
                if response.status_code == 401:
                    raise GoogleDriveAuthenticationError("Credenciales inválidas o expiradas")
                elif response.status_code == 403:
                    raise GoogleDrivePermissionError(
                        "Permisos insuficientes para descargar el archivo"
                    )
                elif response.status_code == 404:
                    raise GoogleDriveNotFoundError(f"Archivo no encontrado: {file_id}")
                elif response.status_code == 429:
                    raise GoogleDriveQuotaExceededError()
                elif response.status_code >= 500:
                    raise GoogleDriveAPIError(
                        f"Error del servidor de Google Drive: {response.status_code}",
                        status_code=response.status_code,
                    )
                elif not response.is_success:
                    raise GoogleDriveAPIError(
                        f"Error descargando archivo: HTTP {response.status_code}",
                        status_code=response.status_code,
                    )

                return response.content

        except httpx.TimeoutException:
            raise GoogleDriveTimeoutError()
        except httpx.RequestError as e:
            raise GoogleDriveAPIError(f"Error de conexión: {str(e)}")

    # =========================================================================
    # MÉTODOS PÚBLICOS
    # =========================================================================

    async def get_file_metadata(self, file_id: str) -> DriveFileMetadata:
        """
        Obtiene los metadatos de un archivo.

        Args:
            file_id: ID del archivo en Google Drive

        Returns:
            DriveFileMetadata con los metadatos del archivo

        Raises:
            GoogleDriveNotFoundError: Si el archivo no existe
            GoogleDriveAPIError: En caso de otro error
        """
        params = {
            "fields": "id,name,mimeType,size,createdTime,modifiedTime,parents,webViewLink,webContentLink",
        }

        data = await self._request("GET", f"/files/{file_id}", params=params)

        # Parsear fechas
        if data.get("createdTime"):
            data["created_time"] = datetime.fromisoformat(
                data["createdTime"].replace("Z", "+00:00")
            )
        if data.get("modifiedTime"):
            data["modified_time"] = datetime.fromisoformat(
                data["modifiedTime"].replace("Z", "+00:00")
            )

        return DriveFileMetadata(**data)

    async def list_files(
        self,
        folder_id: str,
        page_size: int = 100,
        page_token: Optional[str] = None,
    ) -> DriveFileListResponse:
        """
        Lista archivos en una carpeta.

        Args:
            folder_id: ID de la carpeta
            page_size: Tamaño de página (máx 1000)
            page_token: Token para la siguiente página

        Returns:
            DriveFileListResponse con lista de archivos

        Raises:
            GoogleDriveAPIError: En caso de error
        """
        params = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "fields": "nextPageToken,files(id,name,mimeType,size,createdTime,modifiedTime,parents,webViewLink,webContentLink)",
            "pageSize": min(page_size, 1000),
            "orderBy": "createdTime desc",
        }

        if page_token:
            params["pageToken"] = page_token

        data = await self._request("GET", "/files", params=params)

        # Parsear fechas para cada archivo
        files = []
        for file_data in data.get("files", []):
            if file_data.get("createdTime"):
                file_data["created_time"] = datetime.fromisoformat(
                    file_data["createdTime"].replace("Z", "+00:00")
                )
            if file_data.get("modifiedTime"):
                file_data["modified_time"] = datetime.fromisoformat(
                    file_data["modifiedTime"].replace("Z", "+00:00")
                )
            files.append(DriveFileMetadata(**file_data))

        return DriveFileListResponse(
            files=files,
            next_page_token=data.get("nextPageToken"),
        )

    async def download_file(self, file_id: str) -> bytes:
        """
        Descarga el contenido de un archivo.

        Args:
            file_id: ID del archivo a descargar

        Returns:
            Bytes del archivo

        Raises:
            GoogleDriveNotFoundError: Si el archivo no existe
            GoogleDriveAPIError: En caso de otro error
        """
        return await self._download_request(file_id)

    async def download_file_as_stream(self, file_id: str) -> BinaryIO:
        """
        Descarga un archivo y retorna un stream de bytes.

        Args:
            file_id: ID del archivo a descargar

        Returns:
            BytesIO stream con el contenido del archivo

        Raises:
            GoogleDriveAPIError: En caso de error
        """
        content = await self.download_file(file_id)
        return BytesIO(content)


# =============================================================================
# SINGLETON / DEPENDENCY INJECTION
# =============================================================================

_google_drive_client: Optional[GoogleDriveClient] = None


def get_google_drive_client() -> GoogleDriveClient:
    """
    Obtiene una instancia singleton del cliente de Google Drive.

    Usar esta función para inyección de dependencias.

    Returns:
        GoogleDriveClient configurado

    Example:
        >>> from src.shared.infrastructure.external_apis.google_drive import get_google_drive_client
        >>> client = get_google_drive_client()
        >>> metadata = await client.get_file_metadata("file_id")
    """
    global _google_drive_client
    if _google_drive_client is None:
        _google_drive_client = GoogleDriveClient()
    return _google_drive_client


def reset_google_drive_client() -> None:
    """Resetea el cliente singleton (útil para tests)."""
    global _google_drive_client
    _google_drive_client = None
