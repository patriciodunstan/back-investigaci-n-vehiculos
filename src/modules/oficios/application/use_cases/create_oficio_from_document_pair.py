"""
Caso de uso: Crear Oficio desde Par de Documentos (Local Storage).

Combina datos extraídos de documentos PDF (Oficio + CAV) con datos
de Boostr API y crea un oficio completo en el sistema.
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
from src.shared.infrastructure.external_apis.boostr import get_boostr_client
from src.shared.infrastructure.external_apis.boostr.schemas import (
    VehicleExtendedInfo,
    PersonInfo,
)
from src.shared.infrastructure.external_apis.boostr.exceptions import (
    BoostrAPIError,
    BoostrNotFoundError,
)
from src.shared.infrastructure.services import get_file_storage


logger = logging.getLogger(__name__)


class CreateOficioFromDocumentPairUseCase:
    """
    Caso de uso para crear un oficio desde un par de documentos (Oficio + CAV).

    Combina datos de:
    - PDFs parseados (Oficio + CAV)
    - Boostr API (enriquecimiento)

    Crea el oficio usando CreateOficioUseCase.
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

        # Enriquecer datos con Boostr (opcional)
        vehiculo_boostr: Optional[VehicleExtendedInfo] = None
        propietario_boostr: Optional[PersonInfo] = None

        try:
            boostr_client = get_boostr_client()

            # Obtener información del vehículo
            if par_dto.cav_extraido.patente:
                try:
                    vehiculo_boostr = await boostr_client.get_vehicle_info(
                        par_dto.cav_extraido.patente
                    )
                    logger.info(
                        f"Datos de vehículo obtenidos de Boostr para {par_dto.cav_extraido.patente}"
                    )
                except (BoostrNotFoundError, BoostrAPIError) as e:
                    logger.warning(f"No se pudo obtener datos de Boostr para vehículo: {e}")

            # Obtener información del propietario
            if par_dto.oficio_extraido.rut_propietario:
                try:
                    propietario_boostr = await boostr_client.get_person_info(
                        par_dto.oficio_extraido.rut_propietario
                    )
                    logger.info(
                        f"Datos de propietario obtenidos de Boostr para {par_dto.oficio_extraido.rut_propietario}"
                    )
                except (BoostrNotFoundError, BoostrAPIError) as e:
                    logger.warning(f"No se pudo obtener datos de Boostr para propietario: {e}")

        except Exception as e:
            logger.warning(f"Error al consultar Boostr (continuando sin enriquecimiento): {e}")

        # Combinar datos según prioridades (Boostr > CAV > Oficio)
        vehiculo_dto = self._combinar_datos_vehiculo(par_dto.cav_extraido, vehiculo_boostr)
        propietario_dto = self._combinar_datos_propietario(
            par_dto.oficio_extraido, propietario_boostr
        )
        direcciones_dto = self._combinar_direcciones(par_dto.oficio_extraido)

        # Crear CreateOficioDTO
        create_dto = CreateOficioDTO(
            numero_oficio=par_dto.oficio_extraido.numero_oficio,
            buffet_id=par_dto.buffet_id or 1,  # Default si no hay mapeo
            vehiculo=vehiculo_dto,
            prioridad=PrioridadEnum.MEDIA,  # Default
            fecha_limite=None,
            notas_generales=par_dto.oficio_extraido.contexto_legal,
            propietarios=[propietario_dto] if propietario_dto else None,
            direcciones=direcciones_dto if direcciones_dto else None,
        )

        # Crear oficio usando CreateOficioUseCase
        oficio_response = await self._create_oficio_use_case.execute(create_dto)

        logger.info(
            f"Oficio creado desde local storage: {oficio_response.numero_oficio} "
            f"(ID: {oficio_response.id})"
        )

        # Guardar PDFs como adjuntos
        if par_dto.pdf_bytes_oficio or par_dto.pdf_bytes_cav:
            await self._guardar_pdfs_como_adjuntos(
                oficio_response.id,
                par_dto,
            )

        return oficio_response

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

        # Obtener sesión del repositorio (necesario para crear AdjuntoModel)
        # Nota: Esto requiere acceso a la sesión, lo hacemos a través del repository
        session = getattr(self._repository, "_session", None)
        if not session:
            logger.warning("No se pudo obtener sesión para guardar adjuntos")
            return

        try:
            # Guardar PDF del Oficio como adjunto
            if par_dto.pdf_bytes_oficio and par_dto.storage_path_oficio:
                # Usar el storage_path existente o guardar nuevo
                try:
                    # Intentar leer desde storage_path original
                    storage_path_oficio = par_dto.storage_path_oficio
                except:
                    # Si falla, guardar nuevo en carpeta del oficio
                    storage_path_oficio = storage_service.save_file(
                        par_dto.pdf_bytes_oficio,
                        par_dto.file_name_oficio,
                    )

                adjunto_oficio = AdjuntoModel(
                    oficio_id=oficio_id,
                    investigador_id=None,  # No hay investigador en este flujo
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
                # Usar el storage_path existente o guardar nuevo
                try:
                    # Intentar leer desde storage_path original
                    storage_path_cav = par_dto.storage_path_cav
                except:
                    # Si falla, guardar nuevo en carpeta del oficio
                    storage_path_cav = storage_service.save_file(
                        par_dto.pdf_bytes_cav,
                        par_dto.file_name_cav,
                    )

                adjunto_cav = AdjuntoModel(
                    oficio_id=oficio_id,
                    investigador_id=None,  # No hay investigador en este flujo
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
            # No fallar la creación del oficio si falla el guardado de adjuntos

    def _combinar_datos_vehiculo(
        self,
        cav_extraido,
        vehiculo_boostr: Optional[VehicleExtendedInfo] = None,
    ) -> VehiculoDTO:
        """
        Combina datos de vehículo según prioridad: Boostr > CAV.

        Args:
            cav_extraido: Datos extraídos del CAV
            vehiculo_boostr: Datos de Boostr (opcional)

        Returns:
            VehiculoDTO con datos combinados
        """
        patente = cav_extraido.patente  # Siempre del CAV (requerido)

        # Prioridad: Boostr > CAV
        marca = (
            vehiculo_boostr.marca
            if vehiculo_boostr and vehiculo_boostr.marca
            else cav_extraido.marca
        )
        modelo = (
            vehiculo_boostr.modelo
            if vehiculo_boostr and vehiculo_boostr.modelo
            else cav_extraido.modelo
        )
        año = vehiculo_boostr.año if vehiculo_boostr and vehiculo_boostr.año else cav_extraido.año
        color = (
            vehiculo_boostr.color
            if vehiculo_boostr and vehiculo_boostr.color
            else cav_extraido.color
        )
        vin = vehiculo_boostr.vin if vehiculo_boostr and vehiculo_boostr.vin else cav_extraido.vin

        return VehiculoDTO(
            patente=patente,
            marca=marca,
            modelo=modelo,
            año=año,
            color=color,
            vin=vin,
        )

    def _combinar_datos_propietario(
        self,
        oficio_extraido,
        propietario_boostr: Optional[PersonInfo] = None,
    ) -> Optional[PropietarioDTO]:
        """
        Combina datos de propietario según prioridad: Boostr > Oficio.

        Args:
            oficio_extraido: Datos extraídos del Oficio
            propietario_boostr: Datos de Boostr (opcional)

        Returns:
            PropietarioDTO o None si no hay datos suficientes
        """
        # RUT es requerido
        rut = oficio_extraido.rut_propietario
        if not rut:
            return None

        # Nombre: Boostr > Oficio
        # PersonInfo tiene: nombre, nombres, apellido_paterno, apellido_materno
        nombre_completo = None
        if propietario_boostr:
            # Construir nombre completo desde componentes
            partes_nombre = []
            if propietario_boostr.nombres:
                partes_nombre.append(propietario_boostr.nombres)
            if propietario_boostr.apellido_paterno:
                partes_nombre.append(propietario_boostr.apellido_paterno)
            if propietario_boostr.apellido_materno:
                partes_nombre.append(propietario_boostr.apellido_materno)
            if partes_nombre:
                nombre_completo = " ".join(partes_nombre)
            elif propietario_boostr.nombre:
                nombre_completo = propietario_boostr.nombre

        if not nombre_completo:
            nombre_completo = oficio_extraido.nombre_propietario

        if not nombre_completo:
            return None

        # Email y teléfono: No están en PersonInfo, se dejan como None
        email = None
        telefono = None

        # Dirección principal: Del Oficio (primera dirección)
        direccion_principal = None
        if oficio_extraido.direcciones:
            direccion_principal = oficio_extraido.direcciones[0]

        return PropietarioDTO(
            rut=rut,
            nombre_completo=nombre_completo,
            email=email,
            telefono=telefono,
            tipo=TipoPropietarioEnum.PRINCIPAL,
            direccion_principal=direccion_principal,
            notas=None,
        )

    def _combinar_direcciones(self, oficio_extraido) -> list[DireccionDTO]:
        """
        Convierte direcciones extraídas del Oficio a DireccionDTO.

        Args:
            oficio_extraido: Datos extraídos del Oficio

        Returns:
            Lista de DireccionDTO
        """
        direcciones = []

        if not oficio_extraido.direcciones:
            return direcciones

        for direccion_str in oficio_extraido.direcciones:
            # Parsear dirección básica (se puede mejorar en el futuro)
            # Por ahora, asumimos que la dirección está en el string completo
            direcciones.append(
                DireccionDTO(
                    direccion=direccion_str,
                    comuna=None,  # Se puede parsear en el futuro
                    region=None,  # Se puede parsear en el futuro
                    tipo=TipoDireccionEnum.DOMICILIO,
                    notas=None,
                )
            )

        return direcciones
