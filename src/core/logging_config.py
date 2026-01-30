"""
Configuración de logging para la aplicación.

Configura el sistema de logging con formato estructurado,
colores para distinguir niveles, y logs detallados para debugging.
"""

import logging
import sys
from typing import Optional
from datetime import datetime

from src.core.config import get_settings


# =============================================================================
# CONFIGURACIÓN DE COLORES PARA CONSOLA
# =============================================================================

class ColoredFormatter(logging.Formatter):
    """Formatter personalizado con colores para la consola."""

    # Códigos ANSI para colores
    GREY = "\033[90m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"

    # Colores por nivel de log
    COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: MAGENTA,
    }

    def __init__(self, fmt: str = None, use_colors: bool = True):
        super().__init__(fmt or "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        # Formatear el timestamp usando record.created (siempre existe)
        dt = datetime.fromtimestamp(record.created)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Obtener nivel de log con color
        levelname = record.levelname
        if self.use_colors:
            level_color = self.COLORS.get(record.levelno, self.GREY)
            levelname = f"{level_color}{levelname}{self.RESET}"

        # Formatear el mensaje completo
        return f"{formatted_time} | {levelname} | {record.name} | {record.getMessage()}"


# =============================================================================
# CONFIGURACIÓN DE HANDLERS
# =============================================================================

def setup_logging() -> None:
    """
    Configura el sistema de logging para la aplicación.
    
    Crea:
    - Formatters con colores para consola
    - Handlers para stdout
    - Loggers configurados con niveles apropiados
    """
    settings = get_settings()

    # Obtener nivel de log desde configuración
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG)

    # Formatear el mensaje del inicio de logging
    console_formatter = ColoredFormatter(use_colors=True)

    # Configurar handler para stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)

    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.INFO)

    # Mensaje de confirmación
    console_handler.flush()
    logging.info(
        f"{'='*60}\n"
        f"🚀 Logging configurado exitosamente\n"
        f"{'='*60}\n"
        f"📊 Nivel de log: {settings.LOG_LEVEL.upper()}\n"
        f"📅 Ambiente: {settings.ENVIRONMENT.upper()}\n"
        f"{'='*60}\n"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado con el nombre especificado.
    
    Args:
        name: Nombre del logger (usar __name__ del módulo)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


# =============================================================================
# HELPERS PARA LOGGING DE DETALLES
# =============================================================================

def log_http_request(logger: logging.Logger, method: str, url: str, 
                    headers: Optional[dict] = None, params: Optional[dict] = None) -> None:
    """Loguea detalles de una request HTTP saliente."""
    headers_str = ""
    if headers:
        # Solo mostrar headers importantes (X-API-KEY, Authorization)
        important_headers = {k: v for k, v in headers.items() 
                          if k.lower() in ['x-api-key', 'authorization']}
        if important_headers:
            headers_str = " | Headers: " + ", ".join([f"{k}={v[:20]}..." for k, v in important_headers.items()])
    
    params_str = ""
    if params:
        params_str = f" | Params: {params}"
    
    logger.debug(f"📤 HTTP Request: {method} {url}{headers_str}{params_str}")


def log_http_response(logger: logging.Logger, status_code: int, 
                     response_time_ms: float, content_length: int = 0) -> None:
    """Loguea detalles de una response HTTP entrante."""
    status_color = "\033[92m" if 200 <= status_code < 300 else "\033[93m"
    if status_code < 300:
        status_emoji = "✅"
    elif status_code < 400:
        status_emoji = "➡️"
    elif status_code < 500:
        status_emoji = "⚠️"
    else:
        status_emoji = "❌"
    
    logger.info(
        f"📤 HTTP Response: {status_emoji} Status {status_code}{status_color} | "
        f"Tiempo: {response_time_ms:.0f}ms | "
        f"Tamaño: {content_length/1024:.1f}KB"
    )


def log_boostr_request(logger: logging.Logger, endpoint: str, rut: str, 
                     api_url: str = None) -> None:
    """Loguea detalles de una request a la API de Boostr."""
    logger.debug(
        f"🔍 Boostr Request: {endpoint} | RUT: {rut} | API: {api_url or 'api.boostr.cl'}"
    )


def log_boostr_response(logger: logging.Logger, rut: str, 
                        vehicles_count: int = 0, properties_count: int = 0, 
                        deceased: bool = False, credits_remaining: int = 0) -> None:
    """Loguea detalles de una response de la API de Boostr."""
    summary_parts = [f"RUT: {rut}"]
    
    if vehicles_count > 0:
        summary_parts.append(f"🚗 Vehículos: {vehicles_count}")
    if properties_count > 0:
        summary_parts.append(f"🏠 Propiedades: {properties_count}")
    if deceased:
        summary_parts.append(f"💀 Fallecido: Sí")
    if credits_remaining is not None:
        summary_parts.append(f"💳 Créditos: {credits_remaining}")
    
    summary = " | ".join(summary_parts)
    logger.info(f"✅ Boostr Response: {summary}")
