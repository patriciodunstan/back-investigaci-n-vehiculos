"""
Casos de uso para Notificaciones.
"""

from typing import List

from src.modules.notificaciones.application.dtos import (
    CreateNotificacionDTO,
    NotificacionResponseDTO,
)
from src.modules.notificaciones.application.interfaces import INotificacionRepository
from src.modules.notificaciones.infrastructure.email import IEmailService


class SendNotificationUseCase:
    """Envia una notificacion."""

    def __init__(
        self,
        repository: INotificacionRepository,
        email_service: IEmailService,
    ):
        self._repository = repository
        self._email_service = email_service

    async def execute(self, dto: CreateNotificacionDTO) -> NotificacionResponseDTO:
        """
        Crea y envia una notificacion.

        Args:
            dto: Datos de la notificacion

        Returns:
            NotificacionResponseDTO
        """
        # Crear notificacion en BD
        notificacion = await self._repository.create(
            oficio_id=dto.oficio_id,
            tipo=dto.tipo.value,
            destinatario=dto.destinatario,
            asunto=dto.asunto,
            contenido=dto.contenido,
        )

        # Intentar enviar
        try:
            await self._email_service.send_email(
                to=dto.destinatario,
                subject=dto.asunto or "Notificacion",
                body=dto.contenido or "",
            )
            notificacion = await self._repository.marcar_enviada(notificacion.id)
        except Exception as e:
            notificacion = await self._repository.registrar_error(
                notificacion.id,
                str(e),
            )

        return notificacion


class GetNotificacionesUseCase:
    """Obtiene notificaciones de un oficio."""

    def __init__(self, repository: INotificacionRepository):
        self._repository = repository

    async def execute(self, oficio_id: int) -> List[NotificacionResponseDTO]:
        """Obtiene historial de notificaciones."""
        return await self._repository.get_by_oficio(oficio_id)
