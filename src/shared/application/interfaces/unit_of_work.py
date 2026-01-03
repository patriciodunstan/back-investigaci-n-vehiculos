"""
Interface Unit of Work.

Patrón para manejar transacciones de base de datos de forma coherente.

Principios aplicados:
- SRP: Maneja solo la coordinación de transacciones
- DIP: Abstracción para que los use cases no dependan de SQLAlchemy
"""

from abc import ABC, abstractmethod
from typing import Any


class IUnitOfWork(ABC):
    """
    Interface para Unit of Work.

    Coordina operaciones de múltiples repositorios en una sola transacción.

    Example:
        async with uow:
            await uow.buffets.add(nuevo_buffet)
            await uow.usuarios.add(nuevo_usuario)
            await uow.commit()  # Ambos se guardan o ninguno
    """

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Inicia el contexto de la transacción"""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finaliza el contexto (rollback si hay error)"""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Confirma la transacción"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Revierte la transacción"""
        pass
