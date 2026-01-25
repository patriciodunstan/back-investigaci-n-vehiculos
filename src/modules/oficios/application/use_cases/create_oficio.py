"""
Caso de uso: Crear Oficio.
"""

from src.modules.oficios.application.dtos import (
    CreateOficioDTO,
    OficioResponseDTO,
    VehiculoResponseDTO,
    PropietarioResponseDTO,
    DireccionResponseDTO,
)
from src.modules.oficios.application.interfaces import IOficioRepository
from src.modules.oficios.infrastructure.models import (
    OficioModel,
    VehiculoModel,
    PropietarioModel,
    DireccionModel,
)
from src.modules.oficios.domain.exceptions import (
    NumeroOficioAlreadyExistsException,
    VehiculoYaExisteException,
    PropietarioYaExisteException,
)


class CreateOficioUseCase:
    """Caso de uso para crear un nuevo oficio."""

    def __init__(self, repository: IOficioRepository):
        self._repository = repository

    async def execute(self, dto: CreateOficioDTO) -> OficioResponseDTO:
        """Crea un nuevo oficio con vehiculo y opcionalmente propietarios/direcciones."""
        # Verificar que el numero no exista
        if await self._repository.exists_by_numero(dto.numero_oficio):
            raise NumeroOficioAlreadyExistsException(dto.numero_oficio)

        # Crear el oficio
        oficio = OficioModel(
            numero_oficio=dto.numero_oficio.strip().upper(),
            buffet_id=dto.buffet_id,
            prioridad=dto.prioridad,
            fecha_limite=dto.fecha_limite,
            notas_generales=dto.notas_generales,
        )

        oficio_creado = await self._repository.add(oficio)

        # Verificar que la patente no exista ya en el oficio
        patente_normalizada = dto.vehiculo.patente.upper().replace(" ", "").replace("-", "")
        if await self._repository.exists_vehiculo_patente_in_oficio(
            oficio_creado.id,
            patente_normalizada
        ):
            raise VehiculoYaExisteException(dto.vehiculo.patente, oficio_creado.id)

        # Crear vehiculo
        vehiculo = VehiculoModel(
            oficio_id=oficio_creado.id,
            patente=patente_normalizada,
            marca=dto.vehiculo.marca,
            modelo=dto.vehiculo.modelo,
            año=dto.vehiculo.año,
            color=dto.vehiculo.color,
            vin=dto.vehiculo.vin,
        )
        vehiculo_creado = await self._repository.add_vehiculo(vehiculo)

        # Crear propietarios si hay
        propietarios_creados = []
        if dto.propietarios:
            for p in dto.propietarios:
                # Verificar que el RUT no exista ya en el oficio
                if await self._repository.exists_propietario_rut_in_oficio(
                    oficio_creado.id,
                    p.rut
                ):
                    raise PropietarioYaExisteException(p.rut, oficio_creado.id)
                
                prop = PropietarioModel(
                    oficio_id=oficio_creado.id,
                    rut=p.rut,
                    nombre_completo=p.nombre_completo,
                    email=p.email,
                    telefono=p.telefono,
                    tipo=p.tipo,
                    direccion_principal=p.direccion_principal,
                    notas=p.notas,
                )
                propietarios_creados.append(await self._repository.add_propietario(prop))

        # Crear direcciones si hay
        direcciones_creadas = []
        if dto.direcciones:
            for d in dto.direcciones:
                dir_model = DireccionModel(
                    oficio_id=oficio_creado.id,
                    direccion=d.direccion,
                    comuna=d.comuna,
                    region=d.region,
                    tipo=d.tipo,
                    notas=d.notas,
                )
                direcciones_creadas.append(await self._repository.add_direccion(dir_model))

        return OficioResponseDTO(
            id=oficio_creado.id,
            numero_oficio=oficio_creado.numero_oficio,
            buffet_id=oficio_creado.buffet_id,
            buffet_nombre=None,
            investigador_id=oficio_creado.investigador_id,
            investigador_nombre=None,
            estado=oficio_creado.estado.value,
            prioridad=oficio_creado.prioridad.value,
            fecha_ingreso=oficio_creado.fecha_ingreso,
            fecha_limite=oficio_creado.fecha_limite,
            notas_generales=oficio_creado.notas_generales,
            vehiculos=[
                VehiculoResponseDTO(
                    id=vehiculo_creado.id,
                    patente=vehiculo_creado.patente,
                    marca=vehiculo_creado.marca,
                    modelo=vehiculo_creado.modelo,
                    año=vehiculo_creado.año,
                    color=vehiculo_creado.color,
                    vin=vehiculo_creado.vin,
                )
            ],
            propietarios=[
                PropietarioResponseDTO(
                    id=p.id,
                    rut=p.rut,
                    nombre_completo=p.nombre_completo,
                    email=p.email,
                    telefono=p.telefono,
                    tipo=p.tipo.value,
                    direccion_principal=p.direccion_principal,
                    notas=p.notas,
                )
                for p in propietarios_creados
            ],
            direcciones=[
                DireccionResponseDTO(
                    id=d.id,
                    direccion=d.direccion,
                    comuna=d.comuna,
                    region=d.region,
                    tipo=d.tipo.value,
                    verificada=d.verificada,
                    resultado_verificacion=d.resultado_verificacion.value if hasattr(d.resultado_verificacion, 'value') else str(d.resultado_verificacion),
                    fecha_verificacion=d.fecha_verificacion,
                    verificada_por_id=getattr(d, 'verificada_por_id', None),
                    verificada_por_nombre=None,
                    cantidad_visitas=getattr(d, 'cantidad_visitas', 0) or 0,
                    notas=d.notas,
                )
                for d in direcciones_creadas
            ],
            created_at=oficio_creado.created_at,
            updated_at=oficio_creado.updated_at,
        )
