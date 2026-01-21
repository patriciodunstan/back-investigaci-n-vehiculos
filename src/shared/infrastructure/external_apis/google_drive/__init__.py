"""
Google Drive API Client.

Cliente para integración con Google Drive API usando Service Account.
https://developers.google.com/drive/api

Servicios disponibles:
- Descargar archivos desde Google Drive
- Listar archivos en carpetas
- Obtener metadatos de archivos
"""

from .client import GoogleDriveClient, get_google_drive_client, reset_google_drive_client
from .schemas import DriveFileMetadata, DriveFileListResponse
from .exceptions import (
    GoogleDriveAPIError,
    GoogleDriveAuthenticationError,
    GoogleDriveNotFoundError,
    GoogleDrivePermissionError,
    GoogleDriveQuotaExceededError,
    GoogleDriveTimeoutError,
)

__all__ = [
    "GoogleDriveClient",
    "get_google_drive_client",
    "reset_google_drive_client",
    "DriveFileMetadata",
    "DriveFileListResponse",
    "GoogleDriveAPIError",
    "GoogleDriveAuthenticationError",
    "GoogleDriveNotFoundError",
    "GoogleDrivePermissionError",
    "GoogleDriveQuotaExceededError",
    "GoogleDriveTimeoutError",
]
