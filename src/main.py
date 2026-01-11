"""
Punto de entrada de la aplicacion FastAPI.

Sistema de Investigaciones Vehiculares.

Principios aplicados:
- Composition Root: Ensambla toda la aplicacion
- Separation of Concerns: Cada modulo se registra independiente
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import get_settings
from src.core.logging_config import setup_logging, get_logger
from src.shared.presentation.middleware import (
    ErrorHandlerMiddleware,
    LoggingMiddleware,
)

# Importar todos los modelos para que SQLAlchemy los registre
# pylint: disable=wildcard-import,unused-wildcard-import
from src.shared.infrastructure.database.models_registry import *  # noqa: F401, F403

# Importar routers
from src.modules.usuarios.presentation import auth_router, usuarios_router
from src.modules.buffets.presentation import buffet_router
from src.modules.oficios.presentation import oficio_router
from src.modules.investigaciones.presentation import investigacion_router, boostr_router
from src.modules.notificaciones.presentation import notificacion_router


# Configurar logging
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):  # pylint: disable=redefined-outer-name
    """
    Lifecycle manager para la aplicacion.

    Ejecuta codigo al iniciar y al cerrar la app.
    """
    # Startup
    logger.info("Iniciando aplicacion: %s", settings.APP_NAME)
    logger.info("Ambiente: %s", settings.ENVIRONMENT)
    logger.info("Debug: %s", settings.DEBUG)

    yield

    # Shutdown
    logger.info("Cerrando aplicacion...")


# Crear aplicacion
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Sistema de Investigaciones Vehiculares

    API para gestion de investigaciones de vehiculos para estudios juridicos.

    ### Funcionalidades:
    - Autenticacion JWT
    - Gestion de usuarios y roles
    - Gestion de buffets (clientes)
    - Gestion de oficios de investigacion
    - Timeline de actividades
    - Notificaciones automaticas
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# Configurar CORS
# Si BACKEND_CORS_ORIGINS contiene "*" o está vacío, permitir todos los orígenes
cors_origins = settings.BACKEND_CORS_ORIGINS
if "*" in cors_origins or not cors_origins:
    # Permitir todos los orígenes
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # No se puede usar con allow_origins=["*"]
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Permitir solo orígenes específicos
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Agregar middlewares personalizados
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)


# Registrar routers
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(buffet_router)
app.include_router(oficio_router)
app.include_router(investigacion_router)
app.include_router(boostr_router)
app.include_router(notificacion_router)


# Endpoints de sistema
@app.get(
    "/",
    tags=["Sistema"],
    summary="Raiz",
    description="Endpoint raiz de la API",
)
async def root():
    """Endpoint raiz."""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["Sistema"],
    summary="Health Check",
    description="Verifica el estado de la API",
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected",  # TODO: verificar conexion real
    }


@app.get(
    "/info",
    tags=["Sistema"],
    summary="Informacion del sistema",
    description="Retorna informacion general del sistema",
)
async def system_info():
    """Informacion del sistema."""
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "api_version": "v1",
    }


# Manejador de excepciones global (backup)
@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception):
    """Manejador global de excepciones no capturadas."""
    logger.exception("Error no manejado: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Error interno del servidor",
            },
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
