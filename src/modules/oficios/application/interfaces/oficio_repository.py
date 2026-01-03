"""
Interface del repositorio de oficios.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.oficios.infrastructure.models import (
    OficioModel,
    VehiculoModel,
    PropietarioModel,
    DireccionModel,
)
from src.shared.domain.enums import EstadoOficioEnum


class IOficioRepository(ABC):
    """Interface para el repositorio de oficios."""

    @abstractmethod
    async def get_by_id(self, oficio_id: int) -> Optional[OficioModel]:
        """Obtiene un oficio por su ID con relaciones."""
        pass

    @abstractmethod
    async def get_by_numero(self, numero_oficio: str) -> Optional[OficioModel]:
        """Obtiene un oficio por su numero."""
        pass

    @abstractmethod
    async def exists_by_numero(self, numero_oficio: str) -> bool:
        """Verifica si existe un oficio con el numero dado."""
        pass

    @abstractmethod
    async def add(self, oficio: OficioModel) -> OficioModel:
        """Agrega un nuevo oficio."""
        pass

    @abstractmethod
    async def update(self, oficio: OficioModel) -> OficioModel:
        """Actualiza un oficio existente."""
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        buffet_id: Optional[int] = None,
        investigador_id: Optional[int] = None,
        estado: Optional[EstadoOficioEnum] = None,
    ) -> List[OficioModel]:
        """Obtiene lista de oficios con filtros."""
        pass

    @abstractmethod
    async def count(
        self,
        buffet_id: Optional[int] = None,
        investigador_id: Optional[int] = None,
        estado: Optional[EstadoOficioEnum] = None,
    ) -> int:
        """Cuenta el total de oficios con filtros."""
        pass

    @abstractmethod
    async def add_vehiculo(self, vehiculo: VehiculoModel) -> VehiculoModel:
        """Agrega un vehiculo."""
        pass

    @abstractmethod
    async def add_propietario(self, propietario: PropietarioModel) -> PropietarioModel:
        """Agrega un propietario."""
        pass

    @abstractmethod
    async def add_direccion(self, direccion: DireccionModel) -> DireccionModel:
        """Agrega una direccion."""
        pass
