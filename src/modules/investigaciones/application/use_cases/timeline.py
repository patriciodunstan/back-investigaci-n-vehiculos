"""
Casos de uso para Timeline e Investigaciones.
"""

from typing import List

from src.modules.investigaciones.application.dtos import (
    CreateActividadDTO,
    CreateAvistamientoDTO,
    ActividadResponseDTO,
    AvistamientoResponseDTO,
    TimelineItemDTO,
)
from src.modules.investigaciones.application.interfaces import IInvestigacionRepository


class AddActividadUseCase:
    """Agrega actividad al timeline."""

    def __init__(self, repository: IInvestigacionRepository):
        self._repository = repository

    async def execute(self, dto: CreateActividadDTO) -> ActividadResponseDTO:
        """Agrega actividad."""
        return await self._repository.add_actividad(
            oficio_id=dto.oficio_id,
            tipo_actividad=dto.tipo_actividad.value,
            descripcion=dto.descripcion,
            investigador_id=dto.investigador_id,
            resultado=dto.resultado,
            api_externa=dto.api_externa,
            datos_json=dto.datos_json,
        )


class AddAvistamientoUseCase:
    """Agrega avistamiento al timeline."""

    def __init__(self, repository: IInvestigacionRepository):
        self._repository = repository

    async def execute(self, dto: CreateAvistamientoDTO) -> AvistamientoResponseDTO:
        """Agrega avistamiento."""
        return await self._repository.add_avistamiento(
            oficio_id=dto.oficio_id,
            fuente=dto.fuente.value,
            ubicacion=dto.ubicacion,
            fecha_hora=str(dto.fecha_hora) if dto.fecha_hora else None,
            latitud=dto.latitud,
            longitud=dto.longitud,
            notas=dto.notas,
            api_response_id=dto.api_response_id,
            datos_json=dto.datos_json,
        )


class GetTimelineUseCase:
    """Obtiene timeline de un oficio."""

    def __init__(self, repository: IInvestigacionRepository):
        self._repository = repository

    async def execute(
        self,
        oficio_id: int,
        limit: int = 50,
    ) -> List[TimelineItemDTO]:
        """Obtiene timeline."""
        return await self._repository.get_timeline(oficio_id, limit)
