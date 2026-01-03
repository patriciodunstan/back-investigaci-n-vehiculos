"""
Configuración de logging para la aplicación.

Configura el sistema de logging con formato estructurado.
"""

import logging
import sys
from src.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """
    Configura el sistema de logging.

    Llamar al inicio de la aplicación:
        from src.core.logging_config import setup_logging
        setup_logging()
    """
    # Formato del log
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    # Configurar nivel de log
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configurar handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(log_format))

    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )

    logging.info(f"Logging configurado - Nivel: {settings.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado.

    Args:
        name: Nombre del logger (usar __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
