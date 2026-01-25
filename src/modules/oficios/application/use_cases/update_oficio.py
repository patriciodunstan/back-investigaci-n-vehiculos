"""
Casos de uso: Actualizar Oficio.
"""

from src.modules.oficios.application.dtos import (
    UpdateOficioDTO,
    AsignarInvestigadorDTO,
    CambiarEstadoDTO,
    PropietarioDTO,
    DireccionDTO,
    OficioResponseDTO,
    PropietarioResponseDTO,
    DireccionResponseDTO,
)
from src.modules.oficios.application.interfaces import IOficioRepository
from src.modules.oficios.infrastructure.models import PropietarioModel, DireccionModel
from src.modules.oficios.domain.exceptions import (
    OficioNotFoundException,
    OficioYaFinalizadoException,
)
from src.shared.domain.enums import EstadoOficioEnum


class UpdateOficioUseCase:
    """Caso de uso para actualizar un oficio."""

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(self, oficio_id: int, dto: UpdateOficioDTO) -> OficioResponseDTO:
        """Actualiza datos de un oficio."""
        oficio = await self._repository.get_by_id(oficio_id)
        if oficio is None:
            raise OficioNotFoundException(oficio_id)

        if dto.prioridad is not None:
            oficio.prioridad = dto.prioridad
        if dto.fecha_limite is not None:
            oficio.fecha_limite = dto.fecha_limite
        if dto.notas_generales is not None:
            oficio.notas_generales = dto.notas_generales

        oficio_actualizado = await self._repository.update(oficio)

        from src.modules.oficios.application.use_cases.get_oficio import GetOficioUseCase

        get_use_case = GetOficioUseCase(self._repository)
        return await get_use_case.execute_by_id(oficio_actualizado.id)


class AsignarInvestigadorUseCase:
    """Caso de uso para asignar investigador."""

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(self, oficio_id: int, dto: AsignarInvestigadorDTO) -> OficioResponseDTO:
        """Asigna un investigador al oficio."""
        oficio = await self._repository.get_by_id(oficio_id)
        if oficio is None:
            raise OficioNotFoundException(oficio_id)

        if oficio.estado in (
            EstadoOficioEnum.FINALIZADO_ENCONTRADO,
            EstadoOficioEnum.FINALIZADO_NO_ENCONTRADO,
        ):
            raise OficioYaFinalizadoException(oficio_id)

        oficio.investigador_id = dto.investigador_id
        if oficio.estado == EstadoOficioEnum.PENDIENTE:
            oficio.estado = EstadoOficioEnum.INVESTIGACION

        await self._repository.update(oficio)

        from src.modules.oficios.application.use_cases.get_oficio import GetOficioUseCase

        get_use_case = GetOficioUseCase(self._repository)
        return await get_use_case.execute_by_id(oficio_id)


class CambiarEstadoUseCase:
    """Caso de uso para cambiar estado."""

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(self, oficio_id: int, dto: CambiarEstadoDTO) -> OficioResponseDTO:
        """Cambia el estado de un oficio."""
        oficio = await self._repository.get_by_id(oficio_id)
        if oficio is None:
            raise OficioNotFoundException(oficio_id)

        oficio.estado = dto.estado
        await self._repository.update(oficio)

        from src.modules.oficios.application.use_cases.get_oficio import GetOficioUseCase

        get_use_case = GetOficioUseCase(self._repository)
        return await get_use_case.execute_by_id(oficio_id)


class AgregarPropietarioUseCase:
    """Caso de uso para agregar propietario."""

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(self, oficio_id: int, dto: PropietarioDTO) -> PropietarioResponseDTO:
        """Agrega un propietario a un oficio."""
        oficio = await self._repository.get_by_id(oficio_id)
        if oficio is None:
            raise OficioNotFoundException(oficio_id)

        propietario = PropietarioModel(
            oficio_id=oficio_id,
            rut=dto.rut,
            nombre_completo=dto.nombre_completo,
            email=dto.email,
            telefono=dto.telefono,
            tipo=dto.tipo,
            direccion_principal=dto.direccion_principal,
            notas=dto.notas,
        )

        prop_creado = await self._repository.add_propietario(propietario)

        return PropietarioResponseDTO(
            id=prop_creado.id,
            rut=prop_creado.rut,
            nombre_completo=prop_creado.nombre_completo,
            email=prop_creado.email,
            telefono=prop_creado.telefono,
            tipo=prop_creado.tipo.value,
            direccion_principal=prop_creado.direccion_principal,
            notas=prop_creado.notas,
        )


class AgregarDireccionUseCase:
    """Caso de uso para agregar direccion."""

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(
        self, oficio_id: int, dto: DireccionDTO, agregada_por_id: int = None
    ) -> DireccionResponseDTO:
        """Agrega una direccion a un oficio."""
        oficio = await self._repository.get_by_id(oficio_id)
        if oficio is None:
            raise OficioNotFoundException(oficio_id)

        direccion = DireccionModel(
            oficio_id=oficio_id,
            direccion=dto.direccion,
            comuna=dto.comuna,
            region=dto.region,
            tipo=dto.tipo,
            notas=dto.notas,
            agregada_por_id=agregada_por_id,
        )

        dir_creada = await self._repository.add_direccion(direccion)

        return DireccionResponseDTO(
            id=dir_creada.id,
            direccion=dir_creada.direccion,
            comuna=dir_creada.comuna,
            region=dir_creada.region,
            tipo=dir_creada.tipo.value,
            verificada=dir_creada.verificada,
            resultado_verificacion=dir_creada.resultado_verificacion.value,
            fecha_verificacion=dir_creada.fecha_verificacion,
            verificada_por_id=dir_creada.verificada_por_id,
            verificada_por_nombre=None,
            cantidad_visitas=dir_creada.cantidad_visitas or 0,
            notas=dir_creada.notas,
        )
