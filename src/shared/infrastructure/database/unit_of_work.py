"""
Implementación del patrón Unit of Work.

Coordina transacciones entre múltiples repositorios.

Principios aplicados:
- SRP: Solo coordina transacciones
- DIP: Implementa la interface IUnitOfWork
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.shared.application.interfaces import IUnitOfWork
from src.shared.infrastructure.database.session import AsyncSessionLocal


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

    def __init__(self, session: Optional[AsyncSession] = None):
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
            self._session = AsyncSessionLocal()

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
            await self._session.close()

    async def commit(self) -> None:
        """Confirma la transacción"""
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        """Revierte la transacción"""
        if self._session:
            await self._session.rollback()

    @property
    def session(self) -> AsyncSession:
        """Obtiene la sesión actual"""
        if self._session is None:
            raise RuntimeError("UnitOfWork no está inicializado. Use 'async with'.")
        return self._session
