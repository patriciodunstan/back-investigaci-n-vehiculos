"""
Implementacion SQLAlchemy del repositorio de oficios.
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.modules.oficios.application.interfaces import IOficioRepository
from src.modules.oficios.infrastructure.models import (
    OficioModel,
    VehiculoModel,
    PropietarioModel,
    DireccionModel,
)
from src.modules.oficios.infrastructure.models.direccion_model import (
    VisitaDireccionModel,
)
from src.shared.domain.enums import EstadoOficioEnum


class OficioRepository(IOficioRepository):
    """Repositorio de oficios usando SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, oficio_id: int) -> Optional[OficioModel]:
        """Obtiene oficio por ID con relaciones."""
        stmt = (
            select(OficioModel)
            .where(OficioModel.id == oficio_id)
            .options(
                joinedload(OficioModel.buffet),
                joinedload(OficioModel.investigador),
                joinedload(OficioModel.vehiculos),
                selectinload(OficioModel.propietarios),
                selectinload(OficioModel.direcciones),
            )
        )
        result = await self._session.execute(stmt)
        oficio = result.unique().scalar_one_or_none()

        return oficio

    async def get_by_numero(self, numero_oficio: str) -> Optional[OficioModel]:
        """Obtiene oficio por numero."""
        stmt = select(OficioModel).where(OficioModel.numero_oficio == numero_oficio.upper())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_numero(self, numero_oficio: str) -> bool:
        """Verifica si existe oficio con numero."""
        stmt = (
            select(func.count())
            .select_from(OficioModel)
            .where(OficioModel.numero_oficio == numero_oficio.upper())
        )
        result = await self._session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def add(self, oficio: OficioModel) -> OficioModel:
        """Agrega nuevo oficio."""
        self._session.add(oficio)
        await self._session.flush()
        return oficio

    async def update(self, oficio: OficioModel) -> OficioModel:
        """Actualiza oficio existente."""
        await self._session.flush()
        return oficio

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        buffet_id: Optional[int] = None,
        investigador_id: Optional[int] = None,
        estado: Optional[EstadoOficioEnum] = None,
    ) -> List[OficioModel]:
        """Obtiene lista de oficios con filtros."""
        stmt = select(OficioModel).options(
            joinedload(OficioModel.buffet),
            joinedload(OficioModel.investigador),
            joinedload(OficioModel.vehiculos),
        )

        if buffet_id is not None:
            stmt = stmt.where(OficioModel.buffet_id == buffet_id)
        if investigador_id is not None:
            stmt = stmt.where(OficioModel.investigador_id == investigador_id)
        if estado is not None:
            stmt = stmt.where(OficioModel.estado == estado)

        stmt = stmt.order_by(OficioModel.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        return list(result.unique().scalars().all())

    async def count(
        self,
        buffet_id: Optional[int] = None,
        investigador_id: Optional[int] = None,
        estado: Optional[EstadoOficioEnum] = None,
    ) -> int:
        """Cuenta total de oficios con filtros."""
        stmt = select(func.count(OficioModel.id))

        if buffet_id is not None:
            stmt = stmt.where(OficioModel.buffet_id == buffet_id)
        if investigador_id is not None:
            stmt = stmt.where(OficioModel.investigador_id == investigador_id)
        if estado is not None:
            stmt = stmt.where(OficioModel.estado == estado)

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def add_vehiculo(self, vehiculo: VehiculoModel) -> VehiculoModel:
        """Agrega un vehiculo."""
        self._session.add(vehiculo)
        await self._session.flush()
        return vehiculo

    async def add_propietario(self, propietario: PropietarioModel) -> PropietarioModel:
        """Agrega un propietario."""
        self._session.add(propietario)
        await self._session.flush()
        return propietario

    async def add_direccion(self, direccion: DireccionModel) -> DireccionModel:
        """Agrega una direccion."""
        self._session.add(direccion)
        await self._session.flush()
        return direccion

    async def get_direccion_by_id(self, direccion_id: int) -> Optional[DireccionModel]:
        """Obtiene una dirección por su ID."""
        stmt = (
            select(DireccionModel)
            .where(DireccionModel.id == direccion_id)
            .options(
                joinedload(DireccionModel.oficio),
                joinedload(DireccionModel.verificada_por),
            )
        )
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_direccion(self, direccion: DireccionModel) -> DireccionModel:
        """Actualiza una dirección."""
        await self._session.flush()
        return direccion

    async def add_visita(self, visita: VisitaDireccionModel) -> VisitaDireccionModel:
        """Agrega una visita a una dirección."""
        self._session.add(visita)
        await self._session.flush()
        return visita

    async def get_visitas_by_direccion(self, direccion_id: int) -> List[VisitaDireccionModel]:
        """Obtiene el historial de visitas de una dirección."""
        stmt = (
            select(VisitaDireccionModel)
            .where(VisitaDireccionModel.direccion_id == direccion_id)
            .options(joinedload(VisitaDireccionModel.investigador))
            .order_by(VisitaDireccionModel.fecha_visita.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.unique().scalars().all())
