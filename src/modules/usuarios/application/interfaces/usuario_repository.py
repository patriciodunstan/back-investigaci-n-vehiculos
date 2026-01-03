"""
Interface del repositorio de usuarios.

Define el contrato que debe cumplir cualquier implementacion.

Principios aplicados:
- DIP: Las capas superiores dependen de esta abstraccion
- ISP: Interface especifica para usuarios
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.usuarios.domain.entities import Usuario


class IUsuarioRepository(ABC):
    """
    Interface para el repositorio de usuarios.

    Define las operaciones CRUD y consultas especificas
    que debe implementar cualquier repositorio de usuarios.
    """

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.

        Args:
            user_id: ID del usuario

        Returns:
            Usuario si existe, None en caso contrario
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su email.

        Args:
            email: Email del usuario

        Returns:
            Usuario si existe, None en caso contrario
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica si existe un usuario con el email dado.

        Args:
            email: Email a verificar

        Returns:
            True si existe, False en caso contrario
        """
        pass

    @abstractmethod
    async def add(self, usuario: Usuario) -> Usuario:
        """
        Agrega un nuevo usuario.

        Args:
            usuario: Entidad Usuario a agregar

        Returns:
            Usuario con ID asignado
        """
        pass

    @abstractmethod
    async def update(self, usuario: Usuario) -> Usuario:
        """
        Actualiza un usuario existente.

        Args:
            usuario: Entidad Usuario con datos actualizados

        Returns:
            Usuario actualizado
        """
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
        Elimina un usuario (soft delete).

        Args:
            user_id: ID del usuario a eliminar

        Returns:
            True si se elimino, False si no existia
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        activo_only: bool = True,
    ) -> List[Usuario]:
        """
        Obtiene lista de usuarios con paginacion.

        Args:
            skip: Registros a saltar
            limit: Maximo de registros
            activo_only: Si solo incluir usuarios activos

        Returns:
            Lista de usuarios
        """
        pass

    @abstractmethod
    async def get_by_buffet(
        self,
        buffet_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Usuario]:
        """
        Obtiene usuarios de un buffet especifico.

        Args:
            buffet_id: ID del buffet
            skip: Registros a saltar
            limit: Maximo de registros

        Returns:
            Lista de usuarios del buffet
        """
        pass

    @abstractmethod
    async def count(self, activo_only: bool = True) -> int:
        """
        Cuenta el total de usuarios.

        Args:
            activo_only: Si solo contar usuarios activos

        Returns:
            Numero total de usuarios
        """
        pass
