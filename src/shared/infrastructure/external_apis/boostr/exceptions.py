"""
Excepciones personalizadas para la API de Boostr.

Define errores específicos para manejar diferentes situaciones
de la integración con Boostr.
"""


class BoostrAPIError(Exception):
    """
    Error base para todas las excepciones de Boostr.
    
    Attributes:
        message: Mensaje descriptivo del error
        code: Código de error de Boostr (si aplica)
        status_code: Código HTTP de la respuesta
    """
    
    def __init__(
        self, 
        message: str, 
        code: str = None, 
        status_code: int = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.code:
            parts.append(f"Code: {self.code}")
        if self.status_code:
            parts.append(f"HTTP: {self.status_code}")
        return " | ".join(parts)


class BoostrAuthenticationError(BoostrAPIError):
    """
    Error de autenticación con la API de Boostr.
    
    Se produce cuando:
    - API Key inválida o expirada
    - API Key no proporcionada
    - Sin créditos disponibles
    """
    
    def __init__(self, message: str = "Error de autenticación con Boostr API"):
        super().__init__(message, code="AUTH_ERROR", status_code=401)


class BoostrRateLimitError(BoostrAPIError):
    """
    Error por exceder el límite de requests.
    
    Boostr tiene un límite de 5 requests cada 10 segundos.
    Al excederlo, se bloquea por 1 minuto.
    """
    
    def __init__(
        self, 
        message: str = "Rate limit excedido. Espere 1 minuto.",
        retry_after: int = 60
    ):
        super().__init__(message, code="RATE_LIMIT", status_code=429)
        self.retry_after = retry_after


class BoostrNotFoundError(BoostrAPIError):
    """
    Error cuando no se encuentra el recurso solicitado.
    
    Ejemplos:
    - Patente no encontrada en el registro
    - RUT no existe
    """
    
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, code="NOT_FOUND", status_code=404)


class BoostrValidationError(BoostrAPIError):
    """
    Error de validación de datos de entrada.
    
    Ejemplos:
    - RUT con formato inválido
    - Patente con formato inválido
    """
    
    def __init__(self, message: str = "Datos de entrada inválidos"):
        super().__init__(message, code="VALIDATION_ERROR", status_code=400)


class BoostrTimeoutError(BoostrAPIError):
    """
    Error por timeout en la conexión con Boostr.
    """
    
    def __init__(self, message: str = "Timeout al conectar con Boostr API"):
        super().__init__(message, code="TIMEOUT", status_code=408)


class BoostrServiceUnavailableError(BoostrAPIError):
    """
    Error cuando el servicio de Boostr no está disponible.
    
    Puede ocurrir cuando la fuente original está offline.
    """
    
    def __init__(self, message: str = "Servicio de Boostr no disponible"):
        super().__init__(message, code="SERVICE_UNAVAILABLE", status_code=503)
