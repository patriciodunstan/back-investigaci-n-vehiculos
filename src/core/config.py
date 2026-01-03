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

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

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

    BOOSTR_API_URL: str = ""
    BOOSTR_API_KEY: str = ""
    BOOST_TIMEOUT: int = 30

    CELERITY_BROKER_URL: Optional[str] = None
    CELERITY_RESULT_BACKEND: Optional[str] = None

    LOG_LEVEL: str = "INFO"

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

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
