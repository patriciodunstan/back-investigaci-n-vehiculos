"""
Entidad de Dominio Oficio.

Representa un caso de investigacion vehicular.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.enums import EstadoOficioEnum, PrioridadEnum


@dataclass
class Oficio(BaseEntity):
    """
    Entidad de dominio que representa un oficio de investigacion.

    Attributes:
        numero_oficio: Numero unico del oficio
        buffet_id: ID del buffet solicitante
        investigador_id: ID del investigador asignado
        estado: Estado actual del oficio
        prioridad: Nivel de prioridad
        fecha_ingreso: Fecha de ingreso del oficio
        fecha_limite: Fecha limite para completar
        notas_generales: Notas o comentarios
    """

    numero_oficio: str = ""
    buffet_id: int = 0
    investigador_id: Optional[int] = None
    estado: EstadoOficioEnum = EstadoOficioEnum.PENDIENTE
    prioridad: PrioridadEnum = PrioridadEnum.MEDIA
    fecha_ingreso: date = field(default_factory=date.today)
    fecha_limite: Optional[date] = None
    notas_generales: Optional[str] = None

    @classmethod
    def crear(
        cls,
        numero_oficio: str,
        buffet_id: int,
        prioridad: PrioridadEnum = PrioridadEnum.MEDIA,
        fecha_limite: Optional[date] = None,
        notas_generales: Optional[str] = None,
    ) -> "Oficio":
        """Factory method para crear un nuevo oficio."""
        return cls(
            numero_oficio=numero_oficio.strip().upper(),
            buffet_id=buffet_id,
            estado=EstadoOficioEnum.PENDIENTE,
            prioridad=prioridad,
            fecha_ingreso=date.today(),
            fecha_limite=fecha_limite,
            notas_generales=notas_generales,
        )

    def asignar_investigador(self, investigador_id: int) -> None:
        """Asigna un investigador al oficio."""
        self.investigador_id = investigador_id
        if self.estado == EstadoOficioEnum.PENDIENTE:
            self.estado = EstadoOficioEnum.INVESTIGACION
        self.marcar_actualizado()

    def cambiar_estado(self, nuevo_estado: EstadoOficioEnum) -> None:
        """Cambia el estado del oficio."""
        self.estado = nuevo_estado
        self.marcar_actualizado()

    def cambiar_prioridad(self, nueva_prioridad: PrioridadEnum) -> None:
        """Cambia la prioridad del oficio."""
        self.prioridad = nueva_prioridad
        self.marcar_actualizado()

    def finalizar_encontrado(self) -> None:
        """Marca el oficio como finalizado (vehiculo encontrado)."""
        self.estado = EstadoOficioEnum.FINALIZADO_ENCONTRADO
        self.marcar_actualizado()

    def finalizar_no_encontrado(self) -> None:
        """Marca el oficio como finalizado (vehiculo no encontrado)."""
        self.estado = EstadoOficioEnum.FINALIZADO_NO_ENCONTRADO
        self.marcar_actualizado()

    @property
    def esta_finalizado(self) -> bool:
        """Verifica si el oficio esta finalizado."""
        return self.estado in (
            EstadoOficioEnum.FINALIZADO_ENCONTRADO,
            EstadoOficioEnum.FINALIZADO_NO_ENCONTRADO,
        )

    @property
    def esta_vencido(self) -> bool:
        """Verifica si el oficio esta vencido."""
        if self.fecha_limite is None:
            return False
        return date.today() > self.fecha_limite and not self.esta_finalizado

    @property
    def created_at(self) -> datetime:
        """Alias para compatibilidad."""
        return self.create_at

    @property
    def updated_at(self) -> datetime:
        """Alias para compatibilidad."""
        return self.update_at

    def __repr__(self) -> str:
        return (
            f"<Oficio(id={self.id}, numero='{self.numero_oficio}', "
            f"estado='{self.estado.value}')>"
        )
