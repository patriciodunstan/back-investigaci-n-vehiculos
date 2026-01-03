"""
Interface del repositorio de investigaciones.
"""

from abc import ABC, abstractmethod
from typing import List

from src.modules.investigaciones.application.dtos import (
    ActividadResponseDTO,
    AvistamientoResponseDTO,
    TimelineItemDTO,
)


class IInvestigacionRepository(ABC):
    """Interface para el repositorio de investigaciones."""

    @abstractmethod
    async def add_actividad(
        self,
        oficio_id: int,
        tipo_actividad: str,
        descripcion: str,
        investigador_id: int = None,
        resultado: str = None,
        api_externa: str = None,
        datos_json: str = None,
    ) -> ActividadResponseDTO:
        """Agrega una actividad."""
        pass

    @abstractmethod
    async def add_avistamiento(
        self,
        oficio_id: int,
        fuente: str,
        ubicacion: str,
        fecha_hora: str = None,
        latitud: float = None,
        longitud: float = None,
        notas: str = None,
        api_response_id: str = None,
        datos_json: str = None,
    ) -> AvistamientoResponseDTO:
        """Agrega un avistamiento."""
        pass

    @abstractmethod
    async def get_timeline(
        self,
        oficio_id: int,
        limit: int = 50,
    ) -> List[TimelineItemDTO]:
        """Obtiene el timeline de un oficio."""
        pass

    @abstractmethod
    async def get_actividades(
        self,
        oficio_id: int,
    ) -> List[ActividadResponseDTO]:
        """Obtiene las actividades de un oficio."""
        pass

    @abstractmethod
    async def get_avistamientos(
        self,
        oficio_id: int,
    ) -> List[AvistamientoResponseDTO]:
        """Obtiene los avistamientos de un oficio."""
        pass
