"""
Caso de uso: Crear Oficio desde Par de Documentos (Local Storage).

Combina datos extraídos de documentos PDF (Oficio + CAV) y crea
un oficio completo en el sistema, enriqueciendo con datos de Boostr API.
"""

import logging
from typing import Optional

from src.modules.oficios.application.dtos import (
    ParDocumentoDTO,
    CreateOficioDTO,
    OficioResponseDTO,
    VehiculoDTO,
    PropietarioDTO,
    DireccionDTO,
)
from src.modules.oficios.application.interfaces import IOficioRepository
from src.modules.oficios.application.use_cases.create_oficio import CreateOficioUseCase
from src.modules.oficios.infrastructure.models.adjunto_model import AdjuntoModel
from src.shared.domain.enums import (
    TipoPropietarioEnum,
    TipoDireccionEnum,
    PrioridadEnum,
    TipoAdjuntoEnum,
)
from src.shared.infrastructure.services import get_file_storage
from src.shared.infrastructure.external_apis.boostr import (
    get_boostr_client,
    BoostrAPIError,
    PersonProperty,
    DeceasedInfo,
)


logger = logging.getLogger(__name__)


class CreateOficioFromDocumentPairUseCase:
    """
    Caso de uso para crear un oficio desde un par de documentos (Oficio + CAV).

    Usa datos extraídos de los PDFs (Oficio + CAV) para crear el oficio.
    Enriquece los datos con información de Boostr API:
    - Propiedades del propietario (direcciones adicionales)
    - Estado de defunción del propietario
    """

    def __init__(self, repository: IOficioRepository):
        """
        Inicializa el caso de uso.

        Args:
            repository: Repositorio de oficios
        """
        self._repository = repository
        self._create_oficio_use_case = CreateOficioUseCase(repository)

    async def execute(self, par_dto: ParDocumentoDTO) -> OficioResponseDTO:
        """
        Crea un oficio desde un par de documentos.

        Args:
            par_dto: Par de documentos con datos extraídos

        Returns:
            OficioResponseDTO con el oficio creado

        Raises:
            ValueError: Si faltan datos esenciales (número de oficio, patente)
            NumeroOficioAlreadyExistsException: Si el oficio ya existe
        """
        # Validar datos esenciales
        if not par_dto.oficio_extraido.numero_oficio:
            raise ValueError("El número de oficio es requerido")

        if not par_dto.cav_extraido.patente:
            raise ValueError("La patente del vehículo es requerida")

        # Obtener RUT del propietario para enriquecer con Boostr
        rut_propietario = par_dto.oficio_extraido.rut_propietario

        # Consultar Boostr para enriquecer datos
        propiedades_boostr: list[PersonProperty] = []
        info_defuncion: Optional[DeceasedInfo] = None

        if rut_propietario:
            propiedades_boostr, info_defuncion = await self._consultar_boostr(rut_propietario)

        # Construir DTOs desde datos de los PDFs + Boostr
        vehiculo_dto = self._construir_vehiculo(par_dto.cav_extraido)
        propietario_dto = self._construir_propietario(
            par_dto.oficio_extraido,
            info_defuncion,
        )
        direcciones_dto = self._construir_direcciones(
            par_dto.oficio_extraido,
            propiedades_boostr,
        )

        # Crear CreateOficioDTO
        create_dto = CreateOficioDTO(
            numero_oficio=par_dto.oficio_extraido.numero_oficio,
            buffet_id=par_dto.buffet_id or 1,
            vehiculo=vehiculo_dto,
            prioridad=PrioridadEnum.MEDIA,
            fecha_limite=None,
            notas_generales=par_dto.oficio_extraido.contexto_legal,
            propietarios=[propietario_dto] if propietario_dto else None,
            direcciones=direcciones_dto if direcciones_dto else None,
        )

        # Crear oficio usando CreateOficioUseCase
        oficio_response = await self._create_oficio_use_case.execute(create_dto)

        logger.info(
            f"Oficio creado desde documentos: {oficio_response.numero_oficio} "
            f"(ID: {oficio_response.id}, direcciones: {len(direcciones_dto)})"
        )

        # Guardar PDFs como adjuntos
        if par_dto.pdf_bytes_oficio or par_dto.pdf_bytes_cav:
            await self._guardar_pdfs_como_adjuntos(
                oficio_response.id,
                par_dto,
            )

        return oficio_response

    async def _consultar_boostr(
        self, rut: str
    ) -> tuple[list[PersonProperty], Optional[DeceasedInfo]]:
        """
        Consulta Boostr API para obtener datos adicionales del propietario.

        Args:
            rut: RUT del propietario

        Returns:
            Tupla con (propiedades, info_defuncion)
        """
        propiedades: list[PersonProperty] = []
        info_defuncion: Optional[DeceasedInfo] = None

        try:
            boostr_client = get_boostr_client()

            # Verificar si el propietario falleció
            try:
                info_defuncion = await boostr_client.check_deceased(rut)
                if info_defuncion.fallecido:
                    logger.warning(
                        f"ALERTA: Propietario {rut} está FALLECIDO "
                        f"(fecha: {info_defuncion.fecha_defuncion})"
                    )
                else:
                    logger.info(f"Propietario {rut} no registra defunción")
            except BoostrAPIError as e:
                logger.warning(f"No se pudo verificar defunción de {rut}: {e}")

            # Obtener propiedades (direcciones adicionales)
            try:
                propiedades = await boostr_client.get_person_properties(rut)
                if propiedades:
                    logger.info(
                        f"Boostr: {len(propiedades)} propiedades encontradas para {rut}"
                    )
                else:
                    logger.info(f"Boostr: No se encontraron propiedades para {rut}")
            except BoostrAPIError as e:
                logger.warning(f"No se pudo obtener propiedades de {rut}: {e}")

        except Exception as e:
            logger.error(f"Error al consultar Boostr para {rut}: {e}")

        return propiedades, info_defuncion

    async def _guardar_pdfs_como_adjuntos(
        self,
        oficio_id: int,
        par_dto: ParDocumentoDTO,
    ) -> None:
        """
        Guarda los PDFs del par de documentos como adjuntos del oficio.

        Args:
            oficio_id: ID del oficio creado
            par_dto: Par de documentos con PDFs
        """
        storage_service = get_file_storage()

        session = getattr(self._repository, "_session", None)
        if not session:
            logger.warning("No se pudo obtener sesión para guardar adjuntos")
            return

        try:
            # Guardar PDF del Oficio como adjunto
            if par_dto.pdf_bytes_oficio and par_dto.storage_path_oficio:
                try:
                    storage_path_oficio = par_dto.storage_path_oficio
                except Exception:
                    storage_path_oficio = storage_service.save_file(
                        par_dto.pdf_bytes_oficio,
                        par_dto.file_name_oficio,
                    )

                adjunto_oficio = AdjuntoModel(
                    oficio_id=oficio_id,
                    investigador_id=None,
                    tipo=TipoAdjuntoEnum.DOCUMENTO,
                    filename=par_dto.file_name_oficio,
                    url=storage_path_oficio,
                    mime_type="application/pdf",
                    tamaño_bytes=len(par_dto.pdf_bytes_oficio),
                    descripcion="Oficio original",
                )
                session.add(adjunto_oficio)
                logger.debug(f"Adjunto de Oficio agregado: {par_dto.file_name_oficio}")

            # Guardar PDF del CAV como adjunto
            if par_dto.pdf_bytes_cav and par_dto.storage_path_cav:
                try:
                    storage_path_cav = par_dto.storage_path_cav
                except Exception:
                    storage_path_cav = storage_service.save_file(
                        par_dto.pdf_bytes_cav,
                        par_dto.file_name_cav,
                    )

                adjunto_cav = AdjuntoModel(
                    oficio_id=oficio_id,
                    investigador_id=None,
                    tipo=TipoAdjuntoEnum.DOCUMENTO,
                    filename=par_dto.file_name_cav,
                    url=storage_path_cav,
                    mime_type="application/pdf",
                    tamaño_bytes=len(par_dto.pdf_bytes_cav),
                    descripcion="CAV - Certificado de Inscripción",
                )
                session.add(adjunto_cav)
                logger.debug(f"Adjunto de CAV agregado: {par_dto.file_name_cav}")

            await session.flush()
            logger.info(f"PDFs guardados como adjuntos para oficio {oficio_id}")

        except Exception as e:
            logger.error(f"Error guardando PDFs como adjuntos: {e}", exc_info=True)

    def _construir_vehiculo(self, cav_extraido) -> VehiculoDTO:
        """
        Construye VehiculoDTO desde datos del CAV.

        Args:
            cav_extraido: Datos extraídos del CAV

        Returns:
            VehiculoDTO con datos del vehículo
        """
        return VehiculoDTO(
            patente=cav_extraido.patente,
            marca=cav_extraido.marca,
            modelo=cav_extraido.modelo,
            año=cav_extraido.año,
            color=cav_extraido.color,
            vin=cav_extraido.vin,
        )

    def _construir_propietario(
        self,
        oficio_extraido,
        info_defuncion: Optional[DeceasedInfo] = None,
    ) -> Optional[PropietarioDTO]:
        """
        Construye PropietarioDTO desde datos del Oficio.

        Si el propietario está fallecido (según Boostr), se agrega
        una nota de alerta.

        Args:
            oficio_extraido: Datos extraídos del Oficio
            info_defuncion: Información de defunción de Boostr

        Returns:
            PropietarioDTO o None si no hay datos suficientes
        """
        rut = oficio_extraido.rut_propietario
        if not rut:
            return None

        nombre_completo = oficio_extraido.nombre_propietario
        if not nombre_completo:
            return None

        direccion_principal = None
        if oficio_extraido.direcciones:
            direccion_principal = oficio_extraido.direcciones[0]

        # Construir nota con alerta de defunción si aplica
        notas = None
        if info_defuncion and info_defuncion.fallecido:
            fecha = info_defuncion.fecha_defuncion or "fecha desconocida"
            notas = f"⚠️ PROPIETARIO FALLECIDO (Boostr: {fecha})"

        return PropietarioDTO(
            rut=rut,
            nombre_completo=nombre_completo,
            email=None,
            telefono=None,
            tipo=TipoPropietarioEnum.PRINCIPAL,
            direccion_principal=direccion_principal,
            notas=notas,
        )

    def _construir_direcciones(
        self,
        oficio_extraido,
        propiedades_boostr: list[PersonProperty],
    ) -> list[DireccionDTO]:
        """
        Convierte direcciones extraídas del Oficio a DireccionDTO
        y agrega propiedades de Boostr como direcciones adicionales.

        Args:
            oficio_extraido: Datos extraídos del Oficio
            propiedades_boostr: Propiedades obtenidas de Boostr API

        Returns:
            Lista de DireccionDTO (del oficio + de Boostr)
        """
        direcciones: list[DireccionDTO] = []
        direcciones_existentes: set[str] = set()

        # 1. Direcciones del Oficio (prioridad)
        if oficio_extraido.direcciones:
            for direccion_str in oficio_extraido.direcciones:
                direccion_normalizada = direccion_str.strip().upper()
                if direccion_normalizada not in direcciones_existentes:
                    direcciones.append(
                        DireccionDTO(
                            direccion=direccion_str,
                            comuna=None,
                            region=None,
                            tipo=TipoDireccionEnum.DOMICILIO,
                            notas="Dirección extraída del oficio",
                        )
                    )
                    direcciones_existentes.add(direccion_normalizada)

        # 2. Direcciones de propiedades Boostr
        for propiedad in propiedades_boostr:
            if not propiedad.direccion:
                continue

            # Construir dirección completa
            direccion_completa = propiedad.direccion
            if propiedad.comuna:
                direccion_completa = f"{direccion_completa}, {propiedad.comuna}"

            direccion_normalizada = direccion_completa.strip().upper()

            # Evitar duplicados
            if direccion_normalizada in direcciones_existentes:
                continue

            # Construir nota con información adicional
            notas_parts = ["Propiedad obtenida de Boostr"]
            if propiedad.rol:
                notas_parts.append(f"Rol: {propiedad.rol}")
            if propiedad.destino:
                notas_parts.append(f"Destino: {propiedad.destino}")
            if propiedad.avaluo:
                notas_parts.append(f"Avalúo: ${propiedad.avaluo:,.0f}")

            direcciones.append(
                DireccionDTO(
                    direccion=direccion_completa,
                    comuna=propiedad.comuna,
                    region=None,
                    tipo=TipoDireccionEnum.DOMICILIO,
                    notas=" | ".join(notas_parts),
                )
            )
            direcciones_existentes.add(direccion_normalizada)

        logger.info(
            f"Direcciones construidas: {len(direcciones)} "
            f"(oficio: {len(oficio_extraido.direcciones or [])}, "
            f"boostr: {len(propiedades_boostr)})"
        )

        return direcciones
