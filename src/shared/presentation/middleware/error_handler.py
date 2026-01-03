"""
Middleware para manejo centralizado de errores.

Convierte excepciones de dominio a respuestas HTTP apropiadas.

Principios aplicados:
- SRP: Solo maneja errores
- OCP: Fácil agregar nuevos tipos de excepciones
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import traceback
import logging

from src.shared.domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    DuplicateEntityException,
    ValidationException,
    BusinessRuleException,
    UnauthorizedException,
)

from src.core.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware que captura excepciones y las convierte a respuestas HTTP.

    Mapeo de excepciones:
    - EntityNotFoundException -> 404 Not Found
    - DuplicateEntityException -> 400 Bad Request
    - ValidationException -> 422 Unprocessable Entity
    - BusinessRuleException -> 400 Bad Request
    - UnauthorizedException -> 403 Forbidden
    - DomainException -> 400 Bad Request
    - Exception (otras) -> 500 Internal Server Error
    """

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except EntityNotFoundException as e:
            return self._create_error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                code=e.code,
                message=e.message,
                details={"entity": e.entity_name, "id": e.entity_id},
            )
        except DuplicateEntityException as e:
            return self._create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code=e.code,
                message=e.message,
                details={"entity": e.entity_name, "field": e.field, "value": e.value},
            )
        except ValidationException as e:
            return self._create_error_response(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code=e.code,
                message=e.message,
                details={"field": e.field} if e.field else None,
            )
        except BusinessRuleException as e:
            return self._create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST, code=e.code, message=e.message
            )
        except UnauthorizedException as e:
            return self._create_error_response(
                status_code=status.HTTP_403_FORBIDDEN, code=e.code, message=e.message
            )
        except DomainException as e:
            return self._create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST, code=e.code, message=e.message
            )
        except Exception as e:

            logger.error(f"Error no manejado: {str(e)}\n{traceback.format_exc()}")
            # En desarrollo, mostrar detalles del error
            if settings.DEBUG:
                return self._create_error_response(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    code="INTERNAL_ERROR",
                    message=str(e),
                    details={"traceback": traceback.format_exc()},
                )

            return self._create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="INTERNAL_ERROR",
                message="Error interno del servidor",
            )

    def _create_error_response(
        self, status_code: int, code: str, message: str, details: dict = None
    ):
        """
        Crea una respuesta JSON de error estandarizada.

        Args:
            status_code: Código HTTP
            code: Código de error interno
            message: Mensaje descriptivo
            details: Detalles adicionales (opcional)

        Returns:
            JSONResponse con formato estándar de error
        """
        content = {
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        }
        if details:
            content["error"]["details"] = details
        return JSONResponse(status_code=status_code, content=content)
