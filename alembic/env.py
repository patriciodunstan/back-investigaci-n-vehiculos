"""
Alembic Environment Configuration.

Este archivo configura el entorno de Alembic para:
1. Cargar la configuración desde variables de entorno
2. Importar todos los modelos SQLAlchemy
3. Ejecutar migraciones online y offline

IMPORTANTE: Importa models_registry para que Alembic detecte todos los modelos.
"""

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool

from alembic import context

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Importar configuración y modelos
from src.core.config import get_settings
from src.shared.infrastructure.database.models_registry import Base  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Cargar la URL de base de datos desde settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    # Convertir para async (aunque en modo offline no se use realmente)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detectar cambios en tipos de columnas
        compare_server_default=True,  # Detectar cambios en defaults
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Ejecuta las migraciones en modo síncrono dentro del contexto async."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Detectar cambios en tipos de columnas
        compare_server_default=True,  # Detectar cambios en defaults
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    # Convertir DATABASE_URL: postgresql:// → postgresql+asyncpg://
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    # Remover parámetros de conexión que asyncpg no acepta directamente en la URL
    # asyncpg maneja SSL y otros parámetros de forma diferente
    if "?" in database_url:
        base_url, params = database_url.split("?", 1)
        # Filtrar parámetros que asyncpg no acepta
        filtered_params = []
        for param in params.split("&"):
            key = param.split("=")[0] if "=" in param else param
            # asyncpg no acepta estos parámetros directamente en la URL
            if key not in ["sslmode", "channel_binding"]:
                filtered_params.append(param)
        if filtered_params:
            database_url = f"{base_url}?{'&'.join(filtered_params)}"
        else:
            database_url = base_url

    connectable = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
        # asyncpg no necesita parámetros adicionales en connect_args para conexiones locales
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
