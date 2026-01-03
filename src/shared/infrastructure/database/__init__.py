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
