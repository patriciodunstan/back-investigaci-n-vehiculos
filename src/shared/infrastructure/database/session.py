"""
Gestión de sesiones de base de datos.

Configura la conexión a PostgreSQL y proporciona sesiones para las operaciones.

Principios aplicados:
- SRP: Solo maneja conexiones de BD
- DIP: Los repositorios reciben la sesión como dependencia
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from src.core.config import get_settings

settings = get_settings()

# Convertir DATABASE_URL: postgresql:// → postgresql+asyncpg://
# SQLite: sqlite:/// → sqlite+aiosqlite:///
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
if async_database_url.startswith("sqlite"):
    async_database_url = async_database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

# Remover parámetros de conexión que asyncpg no acepta (como sslmode, channel_binding)
# asyncpg maneja SSL y otros parámetros de forma diferente
if async_database_url.startswith("postgresql+asyncpg://") and "?" in async_database_url:
    base_url, params = async_database_url.split("?", 1)
    # Filtrar parámetros que asyncpg no acepta directamente en la URL
    filtered_params = []
    for param in params.split("&"):
        key = param.split("=")[0] if "=" in param else param
        # asyncpg no acepta estos parámetros directamente en la URL
        if key not in ["sslmode", "channel_binding"]:
            filtered_params.append(param)
    if filtered_params:
        async_database_url = f"{base_url}?{'&'.join(filtered_params)}"
    else:
        async_database_url = base_url

# Configurar parámetros según el tipo de base de datos
if async_database_url.startswith("sqlite"):
    # SQLite no acepta pool_size, max_overflow, pool_pre_ping
    engine = create_async_engine(
        async_database_url,
        echo=settings.DB_ECHO,
    )
else:
    # PostgreSQL acepta todos los parámetros
    engine = create_async_engine(
        async_database_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        echo=settings.DB_ECHO,
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency de FastAPI para obtener sesión de BD.

    Uso en endpoints:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession: Sesión asíncrona de SQLAlchemy

    Note:
        La sesión se cierra automáticamente al finalizar el request.
        Si no hay excepciones, se hace commit automático.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager para obtener sesión de BD.

    Útil para scripts y tareas donde no hay request de FastAPI.

    Uso:
        async with get_db_context() as db:
            result = await db.execute(select(Item))
            items = result.scalars().all()

    Yields:
        AsyncSession: Sesión asíncrona de SQLAlchemy
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.

    Uso:
        python -c "import asyncio; from src.shared.infrastructure.database.session import init_db; asyncio.run(init_db())"

    Note:
        En producción, usar Alembic para migraciones en lugar de esto.
    """
    from src.shared.infrastructure.database.base import Base

    # Importar todos los modelos para que SQLAlchemy los registre
    # (Estos imports se agregarán cuando creemos los módulos)
    # from src.modules.buffets.infrastructure.models import BuffetModel
    # from src.modules.usuarios.infrastructure.models import UsuarioModel
    # etc.

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Base de datos inicializada")


async def drop_db() -> None:
    """
    Elimina todas las tablas de la base de datos.

    ⚠️ PELIGRO: Solo usar en desarrollo/testing
    """
    from src.shared.infrastructure.database.base import Base

    if settings.is_production:
        raise RuntimeError("No se puede eliminar la BD en producción")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("🗑️ Todas las tablas eliminadas")
