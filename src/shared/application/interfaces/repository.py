"""
Interface base para repositorios.

Define el contrato que deben cumplir todos los repositorios.

Principios aplicados:
- DIP: Las capas superiores dependen de esta abstracción
- ISP: Interface mínima con operaciones CRUD básicas
- LSP: Cualquier implementación debe ser intercambiable
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """
    Interface genérica para repositorios.

    Define operaciones CRUD básicas que todos los repositorios deben implementar.

    Type Parameters:
        T: Tipo de entidad que maneja el repositorio
    """

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """
        Obtiene una entidad por su ID.

        Args:
            id: ID de la entidad

        Returns:
            Optional[T]: La entidad si existe, None si no
        """
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Obtiene una lista paginada de entidades.

        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
        """
        pass

    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        Agrega una nueva entidad.

        Args:
            entity: Entidad a agregar

        Returns:
            T: Entidad con ID asignado
        """
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Actualiza una entidad existente.

        Args:
            entity: Entidad con datos actualizados

        Returns:
            T: Entidad actualizada
        """
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """
        Elimina una entidad por su ID.

        Args:
            id: ID de la entidad a eliminar

        Returns:
            bool: True si se eliminó, False si no existía
        """
        pass
