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

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DB_ECHO,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
        Si no hay excepciones, se hace commit automático.
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
