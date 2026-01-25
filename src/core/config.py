"""
Configuración centralizada de la aplicación.

Usa Pydantic Settings para:
- Cargar variables de entorno
- Validar tipos automáticamente
- Proporcionar valores por defecto

Principios aplicados:
- SRP: Solo maneja configuración
- DIP: Las clases dependen de Settings, no de os.environ directamente
"""

from smtplib import SMTP_PORT
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Settings de la aplicación cargados desde variables de entorno.

    Attributes:
        ENVIRONMENT: Ambiente de ejecución (development, staging, production)
        DEBUG: Modo debug activo
        APP_NAME: Nombre de la aplicación
    """

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Sistema de Investigaciones Vehiculares"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Permitir todos los orígenes por defecto

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@investigaciones.cl"
    SMTP_FROM_NAME: str = "Sistema Investigaciones"

    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE: int = 10485760
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "application/pdf"]

    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None

    # Boostr API (https://docs.boostr.cl/reference)
    BOOSTR_API_URL: str = "https://api.boostr.cl"
    BOOSTR_API_KEY: str = ""
    BOOSTR_TIMEOUT: int = 30

    CELERITY_BROKER_URL: Optional[str] = None
    CELERITY_RESULT_BACKEND: Optional[str] = None

    LOG_LEVEL: str = "DEBUG"  # Cambiar a DEBUG para ver más detalles
    LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"  # Formato legible de logs
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"  # Formato de fecha
    
    # TestSprite (testing automatizado)
    TESTSPRITE_API_KEY: Optional[str] = None

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # =========================================================================
    # PDF PROCESSING & DOCUMENT PAIRING
    # =========================================================================

    PDF_OCR_ENABLED: bool = False
    """Habilita OCR para PDFs escaneados (requiere pytesseract)"""

    PDF_OCR_LANGUAGE: str = "spa"
    """Idioma para OCR (spa=español, eng=inglés)"""

    PDF_MAX_SIZE_MB: int = 10
    """Tamaño máximo de PDF en MB"""

    PDF_PROCESSING_TIMEOUT_SECONDS: int = 300
    """Timeout para procesamiento de PDF (5 minutos)"""

    DOCUMENT_PAIR_TIMEOUT_HOURS: int = 24
    """
    Ventana de tiempo para emparejar documentos (Oficio + CAV).
    Si un documento no encuentra su par en este tiempo, queda en ESPERANDO_PAR.
    """

    ENABLE_BOOSTR_AUTO_INVESTIGATION: bool = True
    """
    Habilita investigación automática con Boostr al crear oficios desde documentos.
    Si es True, al procesar un par de documentos (Oficio + CAV), automáticamente
    se ejecutará la investigación completa del vehículo usando la API de Boostr.
    """

    @property
    def celery_broker(self) -> str:
        """URL del broker de Celery (usa REDIS_URL si no está definido)"""
        return self.CELERITY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        """URL del backend de resultados de Celery"""
        return self.CELERITY_RESULT_BACKEND or self.REDIS_URL

    @property
    def is_development(self) -> bool:
        """
        Verifica si estamos en ambiente de desarrollo
        """
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """
        Verifica si estamos en ambiente de produccion
        """
        return self.ENVIRONMENT == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene instancia cacheada de Settings.

    Usar @lru_cache asegura que Settings se cargue solo una vez,
    mejorando el rendimiento.

    Returns:
        Settings: Instancia de configuración

    Example:
        >>> from src.core.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.DATABASE_URL)
    """
    return Settings()
