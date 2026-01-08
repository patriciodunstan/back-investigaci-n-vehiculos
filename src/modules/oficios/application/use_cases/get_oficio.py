"""
Caso de uso: Obtener Oficios.
"""

from typing import List, Optional

from src.modules.oficios.application.dtos import (
    OficioResponseDTO,
    VehiculoResponseDTO,
    PropietarioResponseDTO,
    DireccionResponseDTO,
)
from src.modules.oficios.application.interfaces import IOficioRepository
from src.modules.oficios.domain.exceptions import OficioNotFoundException
from src.shared.domain.enums import EstadoOficioEnum


class GetOficioUseCase:
    """Caso de uso para obtener oficios."""

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    def _model_to_dto(self, oficio) -> OficioResponseDTO:
        """Convierte modelo a DTO."""
        vehiculo_dto = None
        if oficio.vehiculo:
            vehiculo_dto = VehiculoResponseDTO(
                id=oficio.vehiculo.id,
                patente=oficio.vehiculo.patente,
                marca=oficio.vehiculo.marca,
                modelo=oficio.vehiculo.modelo,
                año=oficio.vehiculo.año,
                color=oficio.vehiculo.color,
                vin=oficio.vehiculo.vin,
            )

        propietarios_dto = []
        if hasattr(oficio, "propietarios"):
            for p in oficio.propietarios:
                propietarios_dto.append(
                    PropietarioResponseDTO(
                        id=p.id,
                        rut=p.rut,
                        nombre_completo=p.nombre_completo,
                        email=p.email,
                        telefono=p.telefono,
                        tipo=p.tipo.value if hasattr(p.tipo, "value") else str(p.tipo),
                        direccion_principal=p.direccion_principal,
                        notas=p.notas,
                    )
                )

        direcciones_dto = []
        if hasattr(oficio, "direcciones"):
            for d in oficio.direcciones:
                verificada_por_nombre = None
                if hasattr(d, "verificada_por") and d.verificada_por:
                    verificada_por_nombre = d.verificada_por.nombre
                
                resultado_verificacion = "pendiente"
                if hasattr(d, "resultado_verificacion") and d.resultado_verificacion:
                    resultado_verificacion = (
                        d.resultado_verificacion.value
                        if hasattr(d.resultado_verificacion, "value")
                        else str(d.resultado_verificacion)
                    )
                
                direcciones_dto.append(
                    DireccionResponseDTO(
                        id=d.id,
                        direccion=d.direccion,
                        comuna=d.comuna,
                        region=d.region,
                        tipo=d.tipo.value if hasattr(d.tipo, "value") else str(d.tipo),
                        verificada=d.verificada,
                        resultado_verificacion=resultado_verificacion,
                        fecha_verificacion=d.fecha_verificacion,
                        verificada_por_id=getattr(d, "verificada_por_id", None),
                        verificada_por_nombre=verificada_por_nombre,
                        cantidad_visitas=getattr(d, "cantidad_visitas", 0) or 0,
                        notas=d.notas,
                    )
                )

        buffet_nombre = None
        if oficio.buffet:
            buffet_nombre = oficio.buffet.nombre

        investigador_nombre = None
        if oficio.investigador:
            investigador_nombre = oficio.investigador.nombre

        return OficioResponseDTO(
            id=oficio.id,
            numero_oficio=oficio.numero_oficio,
            buffet_id=oficio.buffet_id,
            buffet_nombre=buffet_nombre,
            investigador_id=oficio.investigador_id,
            investigador_nombre=investigador_nombre,
            estado=oficio.estado.value if hasattr(oficio.estado, "value") else str(oficio.estado),
            prioridad=(
                oficio.prioridad.value
                if hasattr(oficio.prioridad, "value")
                else str(oficio.prioridad)
            ),
            fecha_ingreso=oficio.fecha_ingreso,
            fecha_limite=oficio.fecha_limite,
            notas_generales=oficio.notas_generales,
            vehiculo=vehiculo_dto,
            propietarios=propietarios_dto,
            direcciones=direcciones_dto,
            created_at=oficio.created_at,
            updated_at=oficio.updated_at,
        )

    async def execute_by_id(self, oficio_id: int) -> OficioResponseDTO:
        """Obtiene un oficio por ID."""
        oficio = await self._repository.get_by_id(oficio_id)
        if oficio is None:
            raise OficioNotFoundException(oficio_id)
        return self._model_to_dto(oficio)

    async def execute_list(
        self,
        skip: int = 0,
        limit: int = 100,
        buffet_id: Optional[int] = None,
        investigador_id: Optional[int] = None,
        estado: Optional[EstadoOficioEnum] = None,
    ) -> List[OficioResponseDTO]:
        """Obtiene lista de oficios con filtros."""
        oficios = await self._repository.get_all(
            skip=skip,
            limit=limit,
            buffet_id=buffet_id,
            investigador_id=investigador_id,
            estado=estado,
        )
        return [self._model_to_dto(o) for o in oficios]
