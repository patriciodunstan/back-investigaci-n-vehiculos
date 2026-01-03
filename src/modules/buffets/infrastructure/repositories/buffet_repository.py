"""
Implementacion SQLAlchemy del repositorio de buffets.
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.modules.buffets.application.interfaces import IBuffetRepository
from src.modules.buffets.domain.entities import Buffet
from src.modules.buffets.infrastructure.models import BuffetModel
from src.shared.domain.value_objects import RutChileno, Email


class BuffetRepository(IBuffetRepository):
    """Repositorio de buffets usando SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def _model_to_entity(self, model: BuffetModel) -> Buffet:
        """Convierte modelo SQLAlchemy a entidad de dominio."""
        buffet = Buffet(
            nombre=model.nombre,
            rut=RutChileno.crear(model.rut),
            email_principal=Email.crear(model.email_principal),
            telefono=model.telefono,
            contacto_nombre=model.contacto_nombre,
            token_tablero=model.token_tablero,
            activo=model.activo,
        )
        buffet.id = model.id
        buffet.create_at = model.created_at
        buffet.update_at = model.updated_at
        return buffet

    async def get_by_id(self, buffet_id: int) -> Optional[Buffet]:
        """Obtiene buffet por ID."""
        stmt = select(BuffetModel).where(BuffetModel.id == buffet_id)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_by_rut(self, rut: str) -> Optional[Buffet]:
        """Obtiene buffet por RUT."""
        stmt = select(BuffetModel).where(BuffetModel.rut == rut)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_by_token(self, token: str) -> Optional[Buffet]:
        """Obtiene buffet por token de tablero."""
        stmt = select(BuffetModel).where(BuffetModel.token_tablero == token)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def exists_by_rut(self, rut: str) -> bool:
        """Verifica si existe buffet con RUT."""
        stmt = select(func.count()).select_from(BuffetModel).where(BuffetModel.rut == rut)
        result = self._session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def add(self, buffet: Buffet) -> Buffet:
        """Agrega nuevo buffet."""
        model = BuffetModel(
            nombre=buffet.nombre,
            rut=buffet.rut_str,
            email_principal=buffet.email_str,
            telefono=buffet.telefono,
            contacto_nombre=buffet.contacto_nombre,
            token_tablero=buffet.token_tablero,
            activo=buffet.activo,
        )

        self._session.add(model)
        self._session.flush()

        return self._model_to_entity(model)

    async def update(self, buffet: Buffet) -> Buffet:
        """Actualiza buffet existente."""
        stmt = select(BuffetModel).where(BuffetModel.id == buffet.id)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Buffet con ID {buffet.id} no encontrado")

        model.nombre = buffet.nombre
        model.email_principal = buffet.email_str
        model.telefono = buffet.telefono
        model.contacto_nombre = buffet.contacto_nombre
        model.token_tablero = buffet.token_tablero
        model.activo = buffet.activo

        self._session.flush()

        return self._model_to_entity(model)

    async def delete(self, buffet_id: int) -> bool:
        """Elimina buffet (soft delete)."""
        stmt = select(BuffetModel).where(BuffetModel.id == buffet_id)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return False

        model.activo = False
        self._session.flush()

        return True

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        activo_only: bool = True,
    ) -> List[Buffet]:
        """Obtiene lista de buffets."""
        stmt = select(BuffetModel)

        if activo_only:
            stmt = stmt.where(BuffetModel.activo == True)  # noqa: E712

        stmt = stmt.offset(skip).limit(limit)

        result = self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def count(self, activo_only: bool = True) -> int:
        """Cuenta total de buffets."""
        stmt = select(func.count(BuffetModel.id))

        if activo_only:
            stmt = stmt.where(BuffetModel.activo == True)  # noqa: E712

        result = self._session.execute(stmt)
        return result.scalar() or 0
