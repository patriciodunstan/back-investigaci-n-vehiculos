"""
Interface del repositorio de notificaciones.
"""

from abc import ABC, abstractmethod
from typing import List

from src.modules.notificaciones.application.dtos import NotificacionResponseDTO


class INotificacionRepository(ABC):
    """Interface para el repositorio de notificaciones."""

    @abstractmethod
    async def create(
        self,
        oficio_id: int,
        tipo: str,
        destinatario: str,
        asunto: str = None,
        contenido: str = None,
    ) -> NotificacionResponseDTO:
        """Crea una notificacion."""
        pass

    @abstractmethod
    async def get_by_oficio(
        self,
        oficio_id: int,
    ) -> List[NotificacionResponseDTO]:
        """Obtiene notificaciones de un oficio."""
        pass

    @abstractmethod
    async def marcar_enviada(
        self,
        notificacion_id: int,
    ) -> NotificacionResponseDTO:
        """Marca notificacion como enviada."""
        pass

    @abstractmethod
    async def registrar_error(
        self,
        notificacion_id: int,
        mensaje: str,
    ) -> NotificacionResponseDTO:
        """Registra error en notificacion."""
        pass
