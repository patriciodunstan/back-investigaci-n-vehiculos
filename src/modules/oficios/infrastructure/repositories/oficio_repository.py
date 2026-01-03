"""
Implementacion SQLAlchemy del repositorio de oficios.
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from src.modules.oficios.application.interfaces import IOficioRepository
from src.modules.oficios.infrastructure.models import (
    OficioModel,
    VehiculoModel,
    PropietarioModel,
    DireccionModel,
)
from src.shared.domain.enums import EstadoOficioEnum


class OficioRepository(IOficioRepository):
    """Repositorio de oficios usando SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    async def get_by_id(self, oficio_id: int) -> Optional[OficioModel]:
        """Obtiene oficio por ID con relaciones."""
        stmt = (
            select(OficioModel)
            .where(OficioModel.id == oficio_id)
            .options(
                joinedload(OficioModel.buffet),
                joinedload(OficioModel.investigador),
                joinedload(OficioModel.vehiculo),
            )
        )
        result = self._session.execute(stmt)
        oficio = result.unique().scalar_one_or_none()

        if oficio:
            # Cargar propietarios y direcciones
            oficio.propietarios.all()
            oficio.direcciones.all()

        return oficio

    async def get_by_numero(self, numero_oficio: str) -> Optional[OficioModel]:
        """Obtiene oficio por numero."""
        stmt = select(OficioModel).where(OficioModel.numero_oficio == numero_oficio.upper())
        result = self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_numero(self, numero_oficio: str) -> bool:
        """Verifica si existe oficio con numero."""
        stmt = (
            select(func.count())
            .select_from(OficioModel)
            .where(OficioModel.numero_oficio == numero_oficio.upper())
        )
        result = self._session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def add(self, oficio: OficioModel) -> OficioModel:
        """Agrega nuevo oficio."""
        self._session.add(oficio)
        self._session.flush()
        return oficio

    async def update(self, oficio: OficioModel) -> OficioModel:
        """Actualiza oficio existente."""
        self._session.flush()
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
            joinedload(OficioModel.vehiculo),
        )

        if buffet_id is not None:
            stmt = stmt.where(OficioModel.buffet_id == buffet_id)
        if investigador_id is not None:
            stmt = stmt.where(OficioModel.investigador_id == investigador_id)
        if estado is not None:
            stmt = stmt.where(OficioModel.estado == estado)

        stmt = stmt.order_by(OficioModel.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = self._session.execute(stmt)
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

        result = self._session.execute(stmt)
        return result.scalar() or 0

    async def add_vehiculo(self, vehiculo: VehiculoModel) -> VehiculoModel:
        """Agrega un vehiculo."""
        self._session.add(vehiculo)
        self._session.flush()
        return vehiculo

    async def add_propietario(self, propietario: PropietarioModel) -> PropietarioModel:
        """Agrega un propietario."""
        self._session.add(propietario)
        self._session.flush()
        return propietario

    async def add_direccion(self, direccion: DireccionModel) -> DireccionModel:
        """Agrega una direccion."""
        self._session.add(direccion)
        self._session.flush()
        return direccion
