"""
Base Entity con campos de auditoría.

Todas las entidades de dominio heredan de esta clase base.

Principios aplicados:
- DRY: Campos comunes definidos una sola vez
- OCP: Extensible mediante herencia
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from abc import ABC


@dataclass
class BaseEntity(ABC):
    """
    Clase base abstracta para todas las entidades del dominio.

    Attributes:
        id: Identificador único (None si no está persistido)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización

    Note:
        Las entidades tienen identidad (id) a diferencia de los Value Objects.
    """

    id: Optional[int] = field(default=None)
    create_at: datetime = field(default_factory=datetime.now)
    update_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Hook para validaciones adicionales en subclasess"""
        pass

    def marcar_actualizado(self) -> None:
        """Actualiza el timestamp de modificación"""
        object.__setattr__(self, "update_at", datetime.now())

    def es_nuevo(self) -> bool:
        """
        Verifica si la entidad aún no ha sido persistida
        """
        return self.id is None

    def __eq__(self, other: object) -> bool:
        """
        Dos entidades son iguales si tienen el mismo ID
        """
        if not isinstance(other, BaseEntity):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Has basado en el ID para uso en sets/dicts
        """
        return hash(self.id) if self.id else hash(id(self))
