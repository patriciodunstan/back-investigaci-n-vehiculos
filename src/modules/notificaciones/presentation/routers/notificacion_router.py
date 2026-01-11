"""
Router de notificaciones.

Endpoints para enviar y consultar notificaciones.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db
from src.modules.notificaciones.application.dtos import CreateNotificacionDTO
from src.modules.notificaciones.application.use_cases import (
    SendNotificationUseCase,
    GetNotificacionesUseCase,
)
from src.modules.notificaciones.infrastructure.repositories import (
    NotificacionRepository,
)
from src.modules.notificaciones.infrastructure.email import MockEmailService
from src.modules.notificaciones.presentation.schemas import (
    CreateNotificacionRequest,
    NotificacionResponse,
    NotificacionListResponse,
)
from src.modules.usuarios.presentation.routers import get_current_user
from src.modules.usuarios.presentation.schemas import UserResponse


router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


def get_notificacion_repository(
    db: AsyncSession = Depends(get_db),
) -> NotificacionRepository:
    """Dependency para obtener el repositorio."""
    return NotificacionRepository(db)


def get_email_service() -> MockEmailService:
    """Dependency para obtener el servicio de email."""
    return MockEmailService()


@router.get(
    "/oficios/{oficio_id}/notificaciones",
    response_model=NotificacionListResponse,
    summary="Obtener notificaciones",
)
async def get_notificaciones(
    oficio_id: int,
    repository: NotificacionRepository = Depends(get_notificacion_repository),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Obtiene el historial de notificaciones de un oficio."""
    use_case = GetNotificacionesUseCase(repository)
    items = await use_case.execute(oficio_id)

    return NotificacionListResponse(
        oficio_id=oficio_id,
        items=[
            NotificacionResponse(
                id=n.id,
                oficio_id=n.oficio_id,
                tipo=n.tipo,
                destinatario=n.destinatario,
                asunto=n.asunto,
                contenido=n.contenido,
                enviada=n.enviada,
                fecha_envio=n.fecha_envio,
                intentos=n.intentos,
                error_mensaje=n.error_mensaje,
                created_at=n.created_at,
            )
            for n in items
        ],
        total=len(items),
    )


@router.post(
    "/oficios/{oficio_id}/notificaciones",
    response_model=NotificacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar notificacion",
)
async def send_notificacion(
    oficio_id: int,
    request: CreateNotificacionRequest,
    repository: NotificacionRepository = Depends(get_notificacion_repository),
    email_service: MockEmailService = Depends(get_email_service),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Envia una notificacion."""
    use_case = SendNotificationUseCase(repository, email_service)

    dto = CreateNotificacionDTO(
        oficio_id=oficio_id,
        tipo=request.tipo,
        destinatario=request.destinatario,
        asunto=request.asunto,
        contenido=request.contenido,
    )

    result = await use_case.execute(dto)

    return NotificacionResponse(
        id=result.id,
        oficio_id=result.oficio_id,
        tipo=result.tipo,
        destinatario=result.destinatario,
        asunto=result.asunto,
        contenido=result.contenido,
        enviada=result.enviada,
        fecha_envio=result.fecha_envio,
        intentos=result.intentos,
        error_mensaje=result.error_mensaje,
        created_at=result.created_at,
    )
