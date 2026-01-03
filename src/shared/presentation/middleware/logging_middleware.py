"""
Middleware para logging de requests.

Registra información de cada request para debugging y monitoreo.

Principios aplicados:
- SRP: Solo registra logs
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging
import uuid

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra información de cada request.

    Logs incluyen:
    - Request ID único
    - Método HTTP
    - URL
    - Tiempo de respuesta
    - Código de estado
    """

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())[:8]

        start_time = time.time()

        request.state.request_id = request_id

        logger.info("[%s] --> %s %s", request_id, request.method, request.url.path)

        response = await call_next(request)

        process_time = time.time() - start_time
        process_time_ms = round(process_time * 1000, 2)

        logger.info("[%s] <-- %s (%sms)", request_id, response.status_code, process_time_ms)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time_ms)

        return response

    def _get_request_id(self, request: Request) -> str:
        return (
            request.state.request_id
            if hasattr(request.state, "request_id")
            else str(uuid.uuid4())[:8]
        )

    def _log_request(self, request_id: str, method: str, url: str):
        logger.info("[%s] --> %s %s", request_id, method, url)

    def _log_response(self, request_id: str, status_code: int, process_time_ms: float):
        logger.info("[%s] <-- %s (%sms)", request_id, status_code, process_time_ms)
