# PARTE 6: SHARED INFRASTRUCTURE

> **Prerrequisito:** Haber completado la Parte 5 (Shared Kernel)  
> **Objetivo:** Crear la infraestructura compartida (DB, middlewares, dependencies)  
> **Tiempo estimado:** 1-2 horas

---

## 1. Base de Datos - SQLAlchemy Base

### 1.1 src/shared/infrastructure/database/base.py

```python
"""
SQLAlchemy Base declarativa.

Define la clase base para todos los modelos SQLAlchemy del proyecto.

Principios aplicados:
- DRY: Configuración común en un solo lugar
- OCP: Los modelos extienden esta base
"""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base, declared_attr


class CustomBase:
    """
    Clase base personalizada con campos de auditoría.
    
    Todos los modelos SQLAlchemy heredarán estos campos automáticamente.
    """
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Genera el nombre de tabla automáticamente desde el nombre de la clase.
        
        Ejemplo: BuffetModel -> buffets
        """
        # Convierte CamelCase a snake_case y pluraliza
        import re
        name = cls.__name__
        # Quitar "Model" del final si existe
        if name.endswith("Model"):
            name = name[:-5]
        # Convertir a snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        # Pluralizar (simple: agregar 's')
        return f"{snake_case}s"
    
    # Campos de auditoría presentes en todas las tablas
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


# Crear la base declarativa con nuestra clase personalizada
Base = declarative_base(cls=CustomBase)


def get_table_name(model_class) -> str:
    """
    Obtiene el nombre de tabla de un modelo.
    
    Args:
        model_class: Clase del modelo SQLAlchemy
        
    Returns:
        str: Nombre de la tabla
    """
    return model_class.__tablename__
```

---

## 2. Conexión a Base de Datos

### 2.1 src/shared/infrastructure/database/session.py

```python
"""
Gestión de sesiones de base de datos.

Configura la conexión a PostgreSQL y proporciona sesiones para las operaciones.

Principios aplicados:
- SRP: Solo maneja conexiones de BD
- DIP: Los repositorios reciben la sesión como dependencia
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
from contextlib import contextmanager

from src.core.config import get_settings

settings = get_settings()


# Crear engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    # Configuración del pool de conexiones
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verificar conexión antes de usar
    echo=settings.DB_ECHO,  # Log de queries SQL (solo en desarrollo)
)

# Factory de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency de FastAPI para obtener sesión de BD.
    
    Uso en endpoints:
        @router.get("/items")
        async def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: Sesión de SQLAlchemy
        
    Note:
        La sesión se cierra automáticamente al finalizar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager para obtener sesión de BD.
    
    Útil para scripts y tareas Celery donde no hay request de FastAPI.
    
    Uso:
        with get_db_context() as db:
            db.query(Item).all()
    
    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    
    Uso:
        python -c "from src.shared.infrastructure.database.session import init_db; init_db()"
    
    Note:
        En producción, usar Alembic para migraciones en lugar de esto.
    """
    from src.shared.infrastructure.database.base import Base
    
    # Importar todos los modelos para que SQLAlchemy los registre
    # (Estos imports se agregarán cuando creemos los módulos)
    # from src.modules.buffets.infrastructure.models import BuffetModel
    # from src.modules.usuarios.infrastructure.models import UsuarioModel
    # etc.
    
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada")


def drop_db() -> None:
    """
    Elimina todas las tablas de la base de datos.
    
    ⚠️ PELIGRO: Solo usar en desarrollo/testing
    """
    from src.shared.infrastructure.database.base import Base
    
    if settings.is_production:
        raise RuntimeError("No se puede eliminar la BD en producción")
    
    Base.metadata.drop_all(bind=engine)
    print("🗑️ Todas las tablas eliminadas")
```

### 2.2 src/shared/infrastructure/database/__init__.py

```python
"""
Módulo de base de datos.

Exporta los componentes principales para acceso a datos.
"""

from .base import Base, get_table_name
from .session import (
    engine,
    SessionLocal,
    get_db,
    get_db_context,
    init_db,
    drop_db,
)

__all__ = [
    "Base",
    "get_table_name",
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_context",
    "init_db",
    "drop_db",
]
```

---

## 3. Unit of Work - Implementación

### 3.1 src/shared/infrastructure/database/unit_of_work.py

```python
"""
Implementación del patrón Unit of Work.

Coordina transacciones entre múltiples repositorios.

Principios aplicados:
- SRP: Solo coordina transacciones
- DIP: Implementa la interface IUnitOfWork
"""

from sqlalchemy.orm import Session
from typing import Optional

from src.shared.application.interfaces import IUnitOfWork
from src.shared.infrastructure.database.session import SessionLocal


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """
    Implementación de Unit of Work usando SQLAlchemy.
    
    Coordina operaciones de múltiples repositorios en una sola transacción.
    
    Example:
        async with SQLAlchemyUnitOfWork() as uow:
            buffet = await uow.buffets.add(nuevo_buffet)
            usuario = await uow.usuarios.add(nuevo_usuario)
            await uow.commit()  # Ambos se guardan o ninguno
    
    Attributes:
        session: Sesión de SQLAlchemy
        buffets: Repositorio de buffets (se agregará en el módulo buffets)
        usuarios: Repositorio de usuarios (se agregará en el módulo usuarios)
        oficios: Repositorio de oficios (se agregará en el módulo oficios)
    """
    
    def __init__(self, session: Optional[Session] = None):
        """
        Inicializa el Unit of Work.
        
        Args:
            session: Sesión existente (opcional). Si no se proporciona, se crea una nueva.
        """
        self._session = session
        self._owns_session = session is None
    
    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        """Inicia el contexto de la transacción"""
        if self._owns_session:
            self._session = SessionLocal()
        
        # Aquí se inicializarán los repositorios cuando los creemos
        # self.buffets = SQLAlchemyBuffetRepository(self._session)
        # self.usuarios = SQLAlchemyUsuarioRepository(self._session)
        # self.oficios = SQLAlchemyOficioRepository(self._session)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Finaliza el contexto de la transacción.
        
        Si hubo una excepción, hace rollback automático.
        """
        if exc_type is not None:
            await self.rollback()
        
        if self._owns_session and self._session:
            self._session.close()
    
    async def commit(self) -> None:
        """Confirma la transacción"""
        if self._session:
            self._session.commit()
    
    async def rollback(self) -> None:
        """Revierte la transacción"""
        if self._session:
            self._session.rollback()
    
    @property
    def session(self) -> Session:
        """Obtiene la sesión actual"""
        if self._session is None:
            raise RuntimeError("UnitOfWork no está inicializado. Use 'async with'.")
        return self._session
```

Actualiza el `__init__.py` de database:

### 3.2 Actualizar src/shared/infrastructure/database/__init__.py

```python
"""
Módulo de base de datos.

Exporta los componentes principales para acceso a datos.
"""

from .base import Base, get_table_name
from .session import (
    engine,
    SessionLocal,
    get_db,
    get_db_context,
    init_db,
    drop_db,
)
from .unit_of_work import SQLAlchemyUnitOfWork

__all__ = [
    "Base",
    "get_table_name",
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_context",
    "init_db",
    "drop_db",
    "SQLAlchemyUnitOfWork",
]
```

---

## 4. Middlewares

### 4.1 src/shared/presentation/middleware/error_handler.py

```python
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
                details={"entity": e.entity_name, "id": e.entity_id}
            )
            
        except DuplicateEntityException as e:
            return self._create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code=e.code,
                message=e.message,
                details={"entity": e.entity_name, "field": e.field, "value": e.value}
            )
            
        except ValidationException as e:
            return self._create_error_response(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code=e.code,
                message=e.message,
                details={"field": e.field} if e.field else None
            )
            
        except BusinessRuleException as e:
            return self._create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code=e.code,
                message=e.message
            )
            
        except UnauthorizedException as e:
            return self._create_error_response(
                status_code=status.HTTP_403_FORBIDDEN,
                code=e.code,
                message=e.message
            )
            
        except DomainException as e:
            return self._create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code=e.code,
                message=e.message
            )
            
        except Exception as e:
            # Log del error completo
            logger.error(
                f"Error no manejado: {str(e)}\n{traceback.format_exc()}"
            )
            
            # En desarrollo, mostrar detalles del error
            if settings.DEBUG:
                return self._create_error_response(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    code="INTERNAL_ERROR",
                    message=str(e),
                    details={"traceback": traceback.format_exc()}
                )
            
            # En producción, mensaje genérico
            return self._create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="INTERNAL_ERROR",
                message="Error interno del servidor"
            )
    
    def _create_error_response(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict = None
    ) -> JSONResponse:
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
            }
        }
        
        if details:
            content["error"]["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=content
        )
```

### 4.2 src/shared/presentation/middleware/logging_middleware.py

```python
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
        # Generar ID único para el request
        request_id = str(uuid.uuid4())[:8]
        
        # Registrar inicio del request
        start_time = time.time()
        
        # Agregar request_id al state para usarlo en otros lugares
        request.state.request_id = request_id
        
        # Log de inicio
        logger.info(
            f"[{request_id}] → {request.method} {request.url.path}"
        )
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular tiempo de respuesta
        process_time = time.time() - start_time
        process_time_ms = round(process_time * 1000, 2)
        
        # Log de fin
        logger.info(
            f"[{request_id}] ← {response.status_code} "
            f"({process_time_ms}ms)"
        )
        
        # Agregar headers de debugging
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time_ms)
        
        return response
```

### 4.3 src/shared/presentation/middleware/__init__.py

```python
"""Middlewares compartidos"""

from .error_handler import ErrorHandlerMiddleware
from .logging_middleware import LoggingMiddleware

__all__ = [
    "ErrorHandlerMiddleware",
    "LoggingMiddleware",
]
```

---

## 5. Dependencies de FastAPI

### 5.1 src/shared/presentation/dependencies/auth.py

```python
"""
Dependencies de autenticación.

Proporciona funciones para obtener el usuario actual y verificar permisos.

Principios aplicados:
- SRP: Solo maneja autenticación
- DIP: Depende de abstracciones (interfaces)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from src.core.config import get_settings
from src.shared.infrastructure.database import get_db

settings = get_settings()

# Esquema OAuth2 para obtener token del header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False  # No lanzar error automático si no hay token
)


async def get_current_user_id(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[int]:
    """
    Obtiene el ID del usuario actual desde el JWT token.
    
    Args:
        token: JWT token del header Authorization
        
    Returns:
        Optional[int]: ID del usuario si el token es válido, None si no hay token
        
    Raises:
        HTTPException: Si el token es inválido o expirado
    """
    if token is None:
        return None
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_auth(
    user_id: Optional[int] = Depends(get_current_user_id)
) -> int:
    """
    Requiere que el usuario esté autenticado.
    
    Uso en endpoints:
        @router.get("/protected")
        async def protected_endpoint(user_id: int = Depends(require_auth)):
            return {"user_id": user_id}
    
    Args:
        user_id: ID del usuario (inyectado por get_current_user_id)
        
    Returns:
        int: ID del usuario autenticado
        
    Raises:
        HTTPException: Si no hay usuario autenticado
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


# Placeholder para cuando tengamos el modelo Usuario
# async def get_current_user(
#     user_id: int = Depends(require_auth),
#     db: Session = Depends(get_db)
# ) -> "Usuario":
#     """Obtiene el usuario completo desde la BD"""
#     from src.modules.usuarios.infrastructure.models import UsuarioModel
#     
#     user = db.query(UsuarioModel).filter(UsuarioModel.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado")
#     if not user.activo:
#         raise HTTPException(status_code=403, detail="Usuario inactivo")
#     
#     return user
```

### 5.2 src/shared/presentation/dependencies/pagination.py

```python
"""
Dependencies de paginación.

Proporciona parámetros comunes de paginación para endpoints de listado.

Principios aplicados:
- DRY: Lógica de paginación en un solo lugar
"""

from fastapi import Query
from dataclasses import dataclass

from src.core.config import get_settings

settings = get_settings()


@dataclass
class PaginationParams:
    """
    Parámetros de paginación.
    
    Attributes:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
    """
    skip: int
    limit: int
    
    @property
    def offset(self) -> int:
        """Alias para skip (más común en SQL)"""
        return self.skip


def get_pagination(
    skip: int = Query(
        default=0, 
        ge=0, 
        description="Número de registros a saltar"
    ),
    limit: int = Query(
        default=None,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description=f"Número máximo de registros (máx: {settings.MAX_PAGE_SIZE})"
    )
) -> PaginationParams:
    """
    Dependency para obtener parámetros de paginación.
    
    Uso en endpoints:
        @router.get("/items")
        async def list_items(
            pagination: PaginationParams = Depends(get_pagination)
        ):
            items = db.query(Item).offset(pagination.skip).limit(pagination.limit).all()
            return items
    
    Args:
        skip: Registros a saltar (default: 0)
        limit: Máximo de registros (default: DEFAULT_PAGE_SIZE)
        
    Returns:
        PaginationParams: Objeto con skip y limit validados
    """
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE
    
    return PaginationParams(skip=skip, limit=limit)
```

### 5.3 src/shared/presentation/dependencies/__init__.py

```python
"""Dependencies compartidas de FastAPI"""

from .auth import (
    oauth2_scheme,
    get_current_user_id,
    require_auth,
)
from .pagination import (
    PaginationParams,
    get_pagination,
)

__all__ = [
    "oauth2_scheme",
    "get_current_user_id",
    "require_auth",
    "PaginationParams",
    "get_pagination",
]
```

---

## 6. Configuración de Logging

### 6.1 src/core/logging_config.py

```python
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
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    
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
```

---

## 7. Docker Compose para Base de Datos

### 7.1 docker-compose.yml (en la raíz del proyecto)

```yaml
version: '3.8'

services:
  # Base de datos PostgreSQL
  db:
    image: postgres:16-alpine
    container_name: investigaciones_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: investigaciones_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis para Celery (lo usaremos más adelante)
  redis:
    image: redis:7-alpine
    container_name: investigaciones_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Adminer - UI para administrar PostgreSQL (opcional)
  adminer:
    image: adminer:latest
    container_name: investigaciones_adminer
    restart: unless-stopped
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  postgres_data:
  redis_data:
```

---

## 8. Archivo .env

### 8.1 Crear .env desde .env.example

```powershell
# Copiar el archivo de ejemplo
Copy-Item .env.example .env

# Editar con tu editor favorito
notepad .env
```

### 8.2 Contenido del .env para desarrollo

```env
# ==================== ENVIRONMENT ====================
ENVIRONMENT=development
DEBUG=true
APP_NAME=Sistema de Investigaciones Vehiculares

# ==================== DATABASE ====================
# Para Docker Compose
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/investigaciones_db

# ==================== REDIS ====================
REDIS_URL=redis://localhost:6379/0

# ==================== SECURITY ====================
# Genera tu clave: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ==================== CORS ====================
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# ==================== LOGGING ====================
LOG_LEVEL=DEBUG
```

---

## 9. Iniciar Base de Datos

### 9.1 Comandos para iniciar

```powershell
# 1. Iniciar PostgreSQL y Redis con Docker
docker-compose up -d db redis

# 2. Verificar que los contenedores estén corriendo
docker-compose ps

# 3. Verificar logs (si hay problemas)
docker-compose logs db

# 4. Probar conexión a PostgreSQL
docker exec -it investigaciones_db psql -U postgres -d investigaciones_db -c "SELECT 1;"
```

### 9.2 Salida esperada

```
     NAME                 COMMAND                  STATUS              PORTS
investigaciones_db       "docker-entrypoint.s…"   Up (healthy)        0.0.0.0:5432->5432/tcp
investigaciones_redis    "docker-entrypoint.s…"   Up (healthy)        0.0.0.0:6379->6379/tcp
```

---

## 10. Verificar la Estructura

Después de crear todos los archivos, tu estructura debería verse así:

```
src/
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── logging_config.py          # NUEVO
├── shared/
│   ├── domain/
│   │   ├── entities/
│   │   ├── exceptions/
│   │   └── value_objects/
│   ├── application/
│   │   ├── interfaces/
│   │   └── events/
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── __init__.py        # NUEVO (actualizado)
│   │   │   ├── base.py            # NUEVO
│   │   │   ├── session.py         # NUEVO
│   │   │   └── unit_of_work.py    # NUEVO
│   │   └── event_bus/
│   └── presentation/
│       ├── middleware/
│       │   ├── __init__.py        # NUEVO
│       │   ├── error_handler.py   # NUEVO
│       │   └── logging_middleware.py  # NUEVO
│       └── dependencies/
│           ├── __init__.py        # NUEVO
│           ├── auth.py            # NUEVO
│           └── pagination.py      # NUEVO
```

---

## 11. Test de Conexión a BD

Crea un script simple para probar la conexión:

### 11.1 scripts/test_db_connection.py

```python
"""
Script para probar la conexión a la base de datos.

Ejecutar: python scripts/test_db_connection.py
"""

import sys
sys.path.insert(0, '.')

from src.core.config import get_settings
from src.shared.infrastructure.database import engine, SessionLocal

def test_connection():
    """Prueba la conexión a PostgreSQL"""
    settings = get_settings()
    
    print(f"🔌 Conectando a: {settings.DATABASE_URL}")
    
    try:
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Conexión exitosa a PostgreSQL")
            
        # Probar sesión
        db = SessionLocal()
        db.execute("SELECT version()")
        version = db.execute("SELECT version()").fetchone()[0]
        print(f"📦 Versión de PostgreSQL: {version[:50]}...")
        db.close()
        
        print("\n✅ Todo funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Asegúrate de que:")
        print("   1. Docker esté corriendo: docker-compose up -d db")
        print("   2. El archivo .env esté configurado correctamente")
        return False

if __name__ == "__main__":
    test_connection()
```

### 11.2 Ejecutar el test

```powershell
# Asegurarse de que la BD esté corriendo
docker-compose up -d db

# Ejecutar el script
python scripts/test_db_connection.py
```

---

## 12. Próximo Paso

Una vez que hayas:
1. ✅ Creado todos los archivos de infraestructura
2. ✅ Iniciado PostgreSQL con Docker
3. ✅ Configurado el archivo .env
4. ✅ Probado la conexión a la BD

El siguiente documento será:

**Parte 7: Módulo Usuarios** - Donde crearemos:
- Entidad Usuario
- Modelo SQLAlchemy
- Repositorio
- Use Cases (crear, autenticar, etc.)
- Endpoints de autenticación
- JWT tokens

¿Listo para continuar? Avísame cuando hayas terminado.

