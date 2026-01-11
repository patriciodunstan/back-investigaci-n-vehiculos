"""
Implementacion SQLAlchemy del repositorio de investigaciones.
"""

from typing import List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.investigaciones.application.interfaces import IInvestigacionRepository
from src.modules.investigaciones.application.dtos import (
    ActividadResponseDTO,
    AvistamientoResponseDTO,
    TimelineItemDTO,
)
from src.modules.investigaciones.infrastructure.models import (
    InvestigacionModel,
    AvistamientoModel,
)
from src.shared.domain.enums import TipoActividadEnum, FuenteAvistamientoEnum


class InvestigacionRepository(IInvestigacionRepository):
    """Repositorio de investigaciones usando SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self._session = session

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
        actividad = InvestigacionModel(
            oficio_id=oficio_id,
            investigador_id=investigador_id,
            tipo_actividad=TipoActividadEnum(tipo_actividad),
            descripcion=descripcion,
            resultado=resultado,
            api_externa=api_externa,
            datos_json=datos_json,
            fecha_actividad=datetime.utcnow(),
        )
        self._session.add(actividad)
        await self._session.flush()

        return ActividadResponseDTO(
            id=actividad.id,
            oficio_id=actividad.oficio_id,
            investigador_id=actividad.investigador_id,
            tipo_actividad=actividad.tipo_actividad.value,
            descripcion=actividad.descripcion,
            resultado=actividad.resultado,
            api_externa=actividad.api_externa,
            datos_json=actividad.datos_json,
            fecha_actividad=actividad.fecha_actividad,
            created_at=actividad.created_at,
        )

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
        fecha = datetime.fromisoformat(fecha_hora) if fecha_hora else datetime.utcnow()

        avistamiento = AvistamientoModel(
            oficio_id=oficio_id,
            fuente=FuenteAvistamientoEnum(fuente),
            fecha_hora=fecha,
            ubicacion=ubicacion,
            latitud=latitud,
            longitud=longitud,
            notas=notas,
            api_response_id=api_response_id,
            datos_json=datos_json,
        )
        self._session.add(avistamiento)
        await self._session.flush()

        return AvistamientoResponseDTO(
            id=avistamiento.id,
            oficio_id=avistamiento.oficio_id,
            fuente=avistamiento.fuente.value,
            fecha_hora=avistamiento.fecha_hora,
            ubicacion=avistamiento.ubicacion,
            latitud=avistamiento.latitud,
            longitud=avistamiento.longitud,
            api_response_id=avistamiento.api_response_id,
            datos_json=avistamiento.datos_json,
            notas=avistamiento.notas,
            created_at=avistamiento.created_at,
        )

    async def get_timeline(
        self,
        oficio_id: int,
        limit: int = 50,
    ) -> List[TimelineItemDTO]:
        """Obtiene el timeline combinado de actividades y avistamientos."""
        # Obtener actividades
        act_stmt = (
            select(InvestigacionModel)
            .where(InvestigacionModel.oficio_id == oficio_id)
            .order_by(InvestigacionModel.fecha_actividad.desc())
            .limit(limit)
        )
        actividades = (await self._session.execute(act_stmt)).unique().scalars().all()

        # Obtener avistamientos
        avist_stmt = (
            select(AvistamientoModel)
            .where(AvistamientoModel.oficio_id == oficio_id)
            .order_by(AvistamientoModel.fecha_hora.desc())
            .limit(limit)
        )
        avistamientos = (await self._session.execute(avist_stmt)).unique().scalars().all()

        # Combinar en timeline
        timeline = []

        for a in actividades:
            timeline.append(
                TimelineItemDTO(
                    tipo="actividad",
                    id=a.id,
                    fecha=a.fecha_actividad,
                    descripcion=a.descripcion,
                    detalle=a.resultado,
                    fuente=a.tipo_actividad.value,
                    investigador_id=a.investigador_id,
                )
            )

        for av in avistamientos:
            timeline.append(
                TimelineItemDTO(
                    tipo="avistamiento",
                    id=av.id,
                    fecha=av.fecha_hora,
                    descripcion=f"Avistamiento en {av.ubicacion}",
                    detalle=av.notas,
                    fuente=av.fuente.value,
                )
            )

        # Ordenar por fecha descendente
        timeline.sort(key=lambda x: x.fecha, reverse=True)

        return timeline[:limit]

    async def get_actividades(
        self,
        oficio_id: int,
    ) -> List[ActividadResponseDTO]:
        """Obtiene las actividades de un oficio."""
        stmt = (
            select(InvestigacionModel)
            .where(InvestigacionModel.oficio_id == oficio_id)
            .order_by(InvestigacionModel.fecha_actividad.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()

        return [
            ActividadResponseDTO(
                id=m.id,
                oficio_id=m.oficio_id,
                investigador_id=m.investigador_id,
                tipo_actividad=m.tipo_actividad.value,
                descripcion=m.descripcion,
                resultado=m.resultado,
                api_externa=m.api_externa,
                datos_json=m.datos_json,
                fecha_actividad=m.fecha_actividad,
                created_at=m.created_at,
            )
            for m in models
        ]

    async def get_avistamientos(
        self,
        oficio_id: int,
    ) -> List[AvistamientoResponseDTO]:
        """Obtiene los avistamientos de un oficio."""
        stmt = (
            select(AvistamientoModel)
            .where(AvistamientoModel.oficio_id == oficio_id)
            .order_by(AvistamientoModel.fecha_hora.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()

        return [
            AvistamientoResponseDTO(
                id=m.id,
                oficio_id=m.oficio_id,
                fuente=m.fuente.value,
                fecha_hora=m.fecha_hora,
                ubicacion=m.ubicacion,
                latitud=m.latitud,
                longitud=m.longitud,
                api_response_id=m.api_response_id,
                datos_json=m.datos_json,
                notas=m.notas,
                created_at=m.created_at,
            )
            for m in models
        ]
