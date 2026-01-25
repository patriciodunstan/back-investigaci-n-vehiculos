"""
Caso de uso: Crear Oficio desde Par de Documentos (Local Storage).

Combina datos extraídos de documentos PDF (Oficio + CAV) y crea
un oficio completo en el sistema.
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


logger = logging.getLogger(__name__)


class CreateOficioFromDocumentPairUseCase:
    """
    Caso de uso para crear un oficio desde un par de documentos (Oficio + CAV).

    Usa datos extraídos de los PDFs (Oficio + CAV) para crear el oficio.
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

        # Construir DTOs desde datos de los PDFs
        vehiculo_dto = self._construir_vehiculo(par_dto.cav_extraido)
        propietario_dto = self._construir_propietario(par_dto.oficio_extraido)
        direcciones_dto = self._construir_direcciones(par_dto.oficio_extraido)

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

    def _construir_propietario(self, oficio_extraido) -> Optional[PropietarioDTO]:
        """
        Construye PropietarioDTO desde datos del Oficio.

        Args:
            oficio_extraido: Datos extraídos del Oficio

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

        return PropietarioDTO(
            rut=rut,
            nombre_completo=nombre_completo,
            email=None,
            telefono=None,
            tipo=TipoPropietarioEnum.PRINCIPAL,
            direccion_principal=direccion_principal,
            notas=None,
        )

    def _construir_direcciones(self, oficio_extraido) -> list[DireccionDTO]:
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
            direcciones.append(
                DireccionDTO(
                    direccion=direccion_str,
                    comuna=None,
                    region=None,
                    tipo=TipoDireccionEnum.DOMICILIO,
                    notas=None,
                )
            )

        return direcciones
