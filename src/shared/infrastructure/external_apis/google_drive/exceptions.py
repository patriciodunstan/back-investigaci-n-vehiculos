"""
Excepciones personalizadas para la API de Google Drive.

Define errores específicos para manejar diferentes situaciones
de la integración con Google Drive API.
"""


class GoogleDriveAPIError(Exception):
    """
    Error base para todas las excepciones de Google Drive.

    Attributes:
        message: Mensaje descriptivo del error
        status_code: Código HTTP de la respuesta (si aplica)
    """

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"HTTP: {self.status_code}")
        return " | ".join(parts)


class GoogleDriveAuthenticationError(GoogleDriveAPIError):
    """
    Error de autenticación con Google Drive API.

    Se produce cuando:
    - Service Account JSON inválido o expirado
    - Permisos insuficientes
    - Credenciales no configuradas
    """

    def __init__(self, message: str = "Error de autenticación con Google Drive API"):
        super().__init__(message, status_code=401)


class GoogleDriveNotFoundError(GoogleDriveAPIError):
    """
    Error cuando no se encuentra el recurso solicitado.

    Ejemplos:
    - Archivo no existe
    - Carpeta no existe
    """

    def __init__(self, message: str = "Recurso no encontrado en Google Drive"):
        super().__init__(message, status_code=404)


class GoogleDrivePermissionError(GoogleDriveAPIError):
    """
    Error de permisos insuficientes.

    Se produce cuando:
    - No se tiene acceso al archivo/carpeta
    - Service Account no tiene permisos compartidos
    """

    def __init__(self, message: str = "Permisos insuficientes para acceder al recurso"):
        super().__init__(message, status_code=403)


class GoogleDriveQuotaExceededError(GoogleDriveAPIError):
    """
    Error cuando se excede la cuota de la API.

    Google Drive tiene límites de requests por día.
    """

    def __init__(self, message: str = "Cuota de Google Drive API excedida"):
        super().__init__(message, status_code=429)


class GoogleDriveTimeoutError(GoogleDriveAPIError):
    """
    Error por timeout en la conexión con Google Drive.
    """

    def __init__(self, message: str = "Timeout al conectar con Google Drive API"):
        super().__init__(message, status_code=408)
