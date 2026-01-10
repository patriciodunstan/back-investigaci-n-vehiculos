"""
Caso de uso para registrar visitas a direcciones.
"""

from datetime import datetime
from typing import Optional

from src.modules.oficios.application.interfaces import IOficioRepository
from src.modules.oficios.application.dtos.oficio_dto import (
    VisitaDireccionDTO,
    VisitaDireccionResponseDTO,
    DireccionResponseDTO,
)
from src.modules.oficios.infrastructure.models.direccion_model import (
    DireccionModel,
    VisitaDireccionModel,
)
from src.modules.oficios.domain.exceptions import DireccionNotFoundException
from src.shared.domain.enums import ResultadoVerificacionEnum


class RegistrarVisitaUseCase:
    """
    Caso de uso para registrar una visita a una dirección.
    
    Registra la visita en el historial y actualiza el estado
    de la dirección según el resultado.
    """

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(
        self,
        direccion_id: int,
        dto: VisitaDireccionDTO,
        investigador_id: int,
    ) -> VisitaDireccionResponseDTO:
        """
        Registra una visita a una dirección.
        
        Args:
            direccion_id: ID de la dirección visitada
            dto: Datos de la visita
            investigador_id: ID del investigador que realiza la visita
        
        Returns:
            VisitaDireccionResponseDTO con los datos de la visita registrada
        
        Raises:
            DireccionNotFoundException: Si la dirección no existe
        """
        # Obtener la dirección
        direccion = await self._repository.get_direccion_by_id(direccion_id)
        if not direccion:
            raise DireccionNotFoundException(direccion_id)
        
        # Crear el registro de visita
        visita = VisitaDireccionModel(
            direccion_id=direccion_id,
            usuario_id=investigador_id,
            fecha_visita=datetime.utcnow(),
            resultado=dto.resultado,
            notas=dto.notas,
            latitud=dto.latitud,
            longitud=dto.longitud,
        )
        
        visita = await self._repository.add_visita(visita)
        
        # Actualizar la dirección con el resultado de la visita
        direccion.verificada = True
        direccion.resultado_verificacion = dto.resultado
        direccion.fecha_verificacion = datetime.utcnow()
        direccion.verificada_por_id = investigador_id
        direccion.cantidad_visitas = (direccion.cantidad_visitas or 0) + 1
        
        # Agregar notas si hay
        if dto.notas:
            nota_visita = f"[{datetime.utcnow().strftime('%d/%m/%Y %H:%M')}] {dto.resultado.value}: {dto.notas}"
            if direccion.notas:
                direccion.notas = f"{direccion.notas}\n{nota_visita}"
            else:
                direccion.notas = nota_visita
        
        await self._repository.update_direccion(direccion)
        
        # Obtener nombre del investigador
        investigador_nombre = None
        if visita.investigador:
            investigador_nombre = visita.investigador.nombre
        
        return VisitaDireccionResponseDTO(
            id=visita.id,
            direccion_id=visita.direccion_id,
            investigador_id=visita.usuario_id,
            investigador_nombre=investigador_nombre,
            fecha_visita=visita.fecha_visita,
            resultado=visita.resultado.value,
            notas=visita.notas,
            latitud=visita.latitud,
            longitud=visita.longitud,
        )


class GetHistorialVisitasUseCase:
    """
    Caso de uso para obtener el historial de visitas de una dirección.
    """

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(self, direccion_id: int) -> list[VisitaDireccionResponseDTO]:
        """
        Obtiene el historial de visitas de una dirección.
        
        Args:
            direccion_id: ID de la dirección
        
        Returns:
            Lista de visitas ordenadas por fecha (más reciente primero)
        """
        # Verificar que la dirección existe
        direccion = await self._repository.get_direccion_by_id(direccion_id)
        if not direccion:
            raise DireccionNotFoundException(direccion_id)
        
        visitas = await self._repository.get_visitas_by_direccion(direccion_id)
        
        return [
            VisitaDireccionResponseDTO(
                id=v.id,
                direccion_id=v.direccion_id,
                investigador_id=v.investigador_id,
                investigador_nombre=v.investigador.nombre if v.investigador else None,
                fecha_visita=v.fecha_visita,
                resultado=v.resultado.value,
                notas=v.notas,
                latitud=v.latitud,
                longitud=v.longitud,
            )
            for v in visitas
        ]


class GetDireccionesPendientesUseCase:
    """
    Caso de uso para obtener direcciones pendientes de verificar de un oficio.
    """

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(self, oficio_id: int) -> list[DireccionResponseDTO]:
        """
        Obtiene las direcciones de un oficio que aún no han sido verificadas
        o que tuvieron un resultado no exitoso.
        
        Args:
            oficio_id: ID del oficio
        
        Returns:
            Lista de direcciones pendientes
        """
        oficio = await self._repository.get_by_id(oficio_id)
        if not oficio:
            return []
        
        # Filtrar direcciones pendientes o con resultado no exitoso
        pendientes = []
        for d in oficio.direcciones:
            if (
                d.resultado_verificacion == ResultadoVerificacionEnum.PENDIENTE
                or d.resultado_verificacion in [
                    ResultadoVerificacionEnum.NO_ENCONTRADO,
                    ResultadoVerificacionEnum.RECHAZO_ATENCION,
                ]
            ):
                verificada_por_nombre = None
                if d.verificada_por:
                    verificada_por_nombre = d.verificada_por.nombre
                
                pendientes.append(
                    DireccionResponseDTO(
                        id=d.id,
                        direccion=d.direccion,
                        comuna=d.comuna,
                        region=d.region,
                        tipo=d.tipo.value,
                        verificada=d.verificada,
                        resultado_verificacion=d.resultado_verificacion.value,
                        fecha_verificacion=d.fecha_verificacion,
                        verificada_por_id=d.verificada_por_id,
                        verificada_por_nombre=verificada_por_nombre,
                        cantidad_visitas=d.cantidad_visitas or 0,
                        notas=d.notas,
                    )
                )
        
        return pendientes
