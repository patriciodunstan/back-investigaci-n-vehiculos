"""
Tests unitarios para la entidad Oficio.

Prueba la lógica de dominio sin dependencias de infraestructura.
"""

import pytest
from datetime import date, timedelta

from src.modules.oficios.domain.entities import Oficio
from src.shared.domain.enums import EstadoOficioEnum, PrioridadEnum


class TestOficioEntity:
    """Tests para la entidad Oficio."""

    def test_crear_oficio_exitoso(self):
        """Oficio se crea correctamente con datos válidos."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        assert oficio.numero_oficio == "OF-2026-001"
        assert oficio.buffet_id == 1
        assert oficio.estado == EstadoOficioEnum.PENDIENTE
        assert oficio.prioridad == PrioridadEnum.MEDIA
        assert oficio.fecha_ingreso == date.today()
        assert oficio.investigador_id is None

    def test_crear_oficio_con_prioridad(self):
        """Oficio se crea con prioridad específica."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-002",
            buffet_id=1,
            prioridad=PrioridadEnum.URGENTE,
        )

        assert oficio.prioridad == PrioridadEnum.URGENTE

    def test_crear_oficio_con_fecha_limite(self):
        """Oficio se crea con fecha límite."""
        fecha_limite = date.today() + timedelta(days=30)
        oficio = Oficio.crear(
            numero_oficio="OF-2026-003",
            buffet_id=1,
            fecha_limite=fecha_limite,
        )

        assert oficio.fecha_limite == fecha_limite

    def test_crear_oficio_normaliza_numero(self):
        """Oficio normaliza número a mayúsculas y sin espacios."""
        oficio = Oficio.crear(
            numero_oficio="  of-2026-001  ",
            buffet_id=1,
        )

        assert oficio.numero_oficio == "OF-2026-001"

    def test_asignar_investigador(self):
        """Asignar investigador cambia estado a INVESTIGACION si estaba PENDIENTE."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        oficio.asignar_investigador(investigador_id=1)

        assert oficio.investigador_id == 1
        assert oficio.estado == EstadoOficioEnum.INVESTIGACION

    def test_asignar_investigador_no_cambia_estado_si_no_esta_pendiente(self):
        """Asignar investigador no cambia estado si no está PENDIENTE."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )
        oficio.cambiar_estado(EstadoOficioEnum.NOTIFICACION)

        oficio.asignar_investigador(investigador_id=1)

        assert oficio.investigador_id == 1
        assert oficio.estado == EstadoOficioEnum.NOTIFICACION

    def test_cambiar_estado(self):
        """Cambiar estado modifica el estado del oficio."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        oficio.cambiar_estado(EstadoOficioEnum.INVESTIGACION)

        assert oficio.estado == EstadoOficioEnum.INVESTIGACION

    def test_cambiar_prioridad(self):
        """Cambiar prioridad modifica la prioridad del oficio."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        oficio.cambiar_prioridad(PrioridadEnum.ALTA)

        assert oficio.prioridad == PrioridadEnum.ALTA

    def test_finalizar_encontrado(self):
        """Finalizar encontrado cambia estado a FINALIZADO_ENCONTRADO."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        oficio.finalizar_encontrado()

        assert oficio.estado == EstadoOficioEnum.FINALIZADO_ENCONTRADO
        assert oficio.esta_finalizado is True

    def test_finalizar_no_encontrado(self):
        """Finalizar no encontrado cambia estado a FINALIZADO_NO_ENCONTRADO."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        oficio.finalizar_no_encontrado()

        assert oficio.estado == EstadoOficioEnum.FINALIZADO_NO_ENCONTRADO
        assert oficio.esta_finalizado is True

    def test_esta_finalizado_property(self):
        """Property esta_finalizado retorna True para estados finalizados."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        assert oficio.esta_finalizado is False

        oficio.finalizar_encontrado()
        assert oficio.esta_finalizado is True

        oficio.finalizar_no_encontrado()
        assert oficio.esta_finalizado is True

    def test_esta_vencido_sin_fecha_limite(self):
        """Oficio sin fecha límite no está vencido."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        assert oficio.esta_vencido is False

    def test_esta_vencido_con_fecha_futura(self):
        """Oficio con fecha límite futura no está vencido."""
        fecha_limite = date.today() + timedelta(days=10)
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
            fecha_limite=fecha_limite,
        )

        assert oficio.esta_vencido is False

    def test_esta_vencido_con_fecha_pasada_no_finalizado(self):
        """Oficio con fecha límite pasada y no finalizado está vencido."""
        fecha_limite = date.today() - timedelta(days=10)
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
            fecha_limite=fecha_limite,
        )

        assert oficio.esta_vencido is True

    def test_esta_vencido_con_fecha_pasada_pero_finalizado(self):
        """Oficio con fecha límite pasada pero finalizado no está vencido."""
        fecha_limite = date.today() - timedelta(days=10)
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
            fecha_limite=fecha_limite,
        )
        oficio.finalizar_encontrado()

        assert oficio.esta_vencido is False

    def test_oficio_marca_actualizado_al_cambiar_estado(self):
        """Cambiar estado marca el oficio como actualizado."""
        oficio = Oficio.crear(
            numero_oficio="OF-2026-001",
            buffet_id=1,
        )

        original_updated_at = oficio.updated_at
        oficio.cambiar_estado(EstadoOficioEnum.INVESTIGACION)

        assert oficio.updated_at > original_updated_at
