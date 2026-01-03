"""
SQLAlchemy Base declarativa.

Define la clase base para todos los modelos SQLAlchemy del proyecto.

Principios aplicados:
- DRY: Configuración común en un solo lugar
- OCP: Los modelos extienden esta base
"""

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func  # pylint: disable=no-name-in-module
from sqlalchemy.orm import declarative_base, declared_attr


class CustomBase:
    """
    Clase base personalizada con campos de auditoría.

    Todos los modelos SQLAlchemy heredarán estos campos automáticamente.
    """

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        """
        Genera el nombre de tabla automáticamente desde el nombre de la clase.

        Ejemplo: BuffetModel -> buffets
        """
        import re

        name = cls.__name__  # pylint: disable=no-member

        if name.endswith("Model"):
            name = name[:-5]

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        snake_case = re.sub("([a-z0-9])([A])", r"\1_\2", s1).lower()
        return f"{snake_case}s"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
        nullable=False,
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
