"""
Implementacion SQLAlchemy del repositorio de notificaciones.
"""

from typing import List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.modules.notificaciones.application.interfaces import INotificacionRepository
from src.modules.notificaciones.application.dtos import NotificacionResponseDTO
from src.modules.notificaciones.infrastructure.models import NotificacionModel
from src.shared.domain.enums import TipoNotificacionEnum


class NotificacionRepository(INotificacionRepository):
    """Repositorio de notificaciones usando SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def _model_to_dto(self, model: NotificacionModel) -> NotificacionResponseDTO:
        """Convierte modelo a DTO."""
        return NotificacionResponseDTO(
            id=model.id,
            oficio_id=model.oficio_id,
            tipo=model.tipo.value,
            destinatario=model.destinatario,
            asunto=model.asunto,
            contenido=model.contenido,
            enviada=model.enviada,
            fecha_envio=model.fecha_envio,
            intentos=model.intentos,
            error_mensaje=model.error_mensaje,
            created_at=model.created_at,
        )

    async def create(
        self,
        oficio_id: int,
        tipo: str,
        destinatario: str,
        asunto: str = None,
        contenido: str = None,
    ) -> NotificacionResponseDTO:
        """Crea una notificacion."""
        notificacion = NotificacionModel(
            oficio_id=oficio_id,
            tipo=TipoNotificacionEnum(tipo),
            destinatario=destinatario,
            asunto=asunto,
            contenido=contenido,
            enviada=False,
            intentos=0,
        )
        self._session.add(notificacion)
        self._session.flush()

        return self._model_to_dto(notificacion)

    async def get_by_oficio(
        self,
        oficio_id: int,
    ) -> List[NotificacionResponseDTO]:
        """Obtiene notificaciones de un oficio."""
        stmt = (
            select(NotificacionModel)
            .where(NotificacionModel.oficio_id == oficio_id)
            .order_by(NotificacionModel.created_at.desc())
        )
        models = self._session.execute(stmt).scalars().all()

        return [self._model_to_dto(m) for m in models]

    async def marcar_enviada(
        self,
        notificacion_id: int,
    ) -> NotificacionResponseDTO:
        """Marca notificacion como enviada."""
        stmt = select(NotificacionModel).where(
            NotificacionModel.id == notificacion_id
        )
        model = self._session.execute(stmt).scalar_one()

        model.enviada = True
        model.fecha_envio = datetime.utcnow()
        self._session.flush()

        return self._model_to_dto(model)

    async def registrar_error(
        self,
        notificacion_id: int,
        mensaje: str,
    ) -> NotificacionResponseDTO:
        """Registra error en notificacion."""
        stmt = select(NotificacionModel).where(
            NotificacionModel.id == notificacion_id
        )
        model = self._session.execute(stmt).scalar_one()

        model.intentos += 1
        model.error_mensaje = mensaje
        self._session.flush()

        return self._model_to_dto(model)

