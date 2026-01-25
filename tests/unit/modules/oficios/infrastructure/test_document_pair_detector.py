"""
Tests unitarios para DocumentPairDetector.

Verifica la lógica de detección de pares de documentos (Oficio + CAV).
"""

import pytest
import uuid
from datetime import datetime, timedelta

from src.modules.oficios.infrastructure.services import DocumentPairDetector
from src.modules.oficios.infrastructure.models.documento_procesado_model import (
    DocumentoProcesadoModel,
)
from src.shared.domain.enums import TipoDocumentoEnum, EstadoDocumentoProcesadoEnum


class TestDocumentPairDetector:
    """Tests para DocumentPairDetector."""

    @pytest.mark.asyncio
    async def test_find_pair_oficio_busca_cav(
        self, db_session, documento_oficio_esperando_par
    ):
        """
        Test que un OFICIO busca un CAV como par complementario.
        """
        # Crear un CAV pendiente del mismo buffet
        cav = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="cav_complemento.pdf",
            storage_path="2024/01/cav_complemento.pdf",
            tipo_documento=TipoDocumentoEnum.CAV,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=documento_oficio_esperando_par.buffet_id,
        )
        db_session.add(cav)
        await db_session.flush()

        detector = DocumentPairDetector(db_session)
        par = await detector.find_pair(
            file_id=documento_oficio_esperando_par.file_id,
            tipo_documento=TipoDocumentoEnum.OFICIO,
            buffet_id=documento_oficio_esperando_par.buffet_id,
        )

        assert par is not None
        assert par.tipo_documento == TipoDocumentoEnum.CAV
        assert par.file_id == cav.file_id

    @pytest.mark.asyncio
    async def test_find_pair_cav_busca_oficio(self, db_session, test_buffet):
        """
        Test que un CAV busca un OFICIO como par complementario.
        """
        # Crear un OFICIO esperando par
        oficio = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="oficio_esperando.pdf",
            storage_path="2024/01/oficio_esperando.pdf",
            tipo_documento=TipoDocumentoEnum.OFICIO,
            estado=EstadoDocumentoProcesadoEnum.ESPERANDO_PAR,
            buffet_id=test_buffet.id,
        )
        db_session.add(oficio)
        await db_session.flush()

        # Crear un CAV
        cav = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="cav_nuevo.pdf",
            storage_path="2024/01/cav_nuevo.pdf",
            tipo_documento=TipoDocumentoEnum.CAV,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=test_buffet.id,
        )
        db_session.add(cav)
        await db_session.flush()

        detector = DocumentPairDetector(db_session)
        par = await detector.find_pair(
            file_id=cav.file_id,
            tipo_documento=TipoDocumentoEnum.CAV,
            buffet_id=test_buffet.id,
        )

        assert par is not None
        assert par.tipo_documento == TipoDocumentoEnum.OFICIO
        assert par.file_id == oficio.file_id

    @pytest.mark.asyncio
    async def test_find_pair_no_encuentra_sin_par(self, db_session, test_buffet):
        """
        Test que retorna None cuando no hay par disponible.
        """
        # Crear un OFICIO sin par
        oficio = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="oficio_solo.pdf",
            storage_path="2024/01/oficio_solo.pdf",
            tipo_documento=TipoDocumentoEnum.OFICIO,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=test_buffet.id,
        )
        db_session.add(oficio)
        await db_session.flush()

        detector = DocumentPairDetector(db_session)
        par = await detector.find_pair(
            file_id=oficio.file_id,
            tipo_documento=TipoDocumentoEnum.OFICIO,
            buffet_id=test_buffet.id,
        )

        assert par is None

    @pytest.mark.asyncio
    async def test_find_pair_ignora_documentos_completados(self, db_session, test_buffet):
        """
        Test que no considera documentos en estado COMPLETADO como pares.
        """
        # Crear un CAV ya completado
        cav_completado = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="cav_completado.pdf",
            storage_path="2024/01/cav_completado.pdf",
            tipo_documento=TipoDocumentoEnum.CAV,
            estado=EstadoDocumentoProcesadoEnum.COMPLETADO,
            buffet_id=test_buffet.id,
        )
        db_session.add(cav_completado)
        await db_session.flush()

        # Crear un OFICIO buscando par
        oficio = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="oficio_buscando.pdf",
            storage_path="2024/01/oficio_buscando.pdf",
            tipo_documento=TipoDocumentoEnum.OFICIO,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=test_buffet.id,
        )
        db_session.add(oficio)
        await db_session.flush()

        detector = DocumentPairDetector(db_session)
        par = await detector.find_pair(
            file_id=oficio.file_id,
            tipo_documento=TipoDocumentoEnum.OFICIO,
            buffet_id=test_buffet.id,
        )

        assert par is None

    @pytest.mark.asyncio
    async def test_find_pair_ignora_documentos_con_error(self, db_session, test_buffet):
        """
        Test que no considera documentos en estado ERROR como pares.
        """
        # Crear un CAV con error
        cav_error = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="cav_error.pdf",
            storage_path="2024/01/cav_error.pdf",
            tipo_documento=TipoDocumentoEnum.CAV,
            estado=EstadoDocumentoProcesadoEnum.ERROR,
            buffet_id=test_buffet.id,
            error_mensaje="Error de prueba",
        )
        db_session.add(cav_error)
        await db_session.flush()

        # Crear un OFICIO buscando par
        oficio = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="oficio_buscando2.pdf",
            storage_path="2024/01/oficio_buscando2.pdf",
            tipo_documento=TipoDocumentoEnum.OFICIO,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=test_buffet.id,
        )
        db_session.add(oficio)
        await db_session.flush()

        detector = DocumentPairDetector(db_session)
        par = await detector.find_pair(
            file_id=oficio.file_id,
            tipo_documento=TipoDocumentoEnum.OFICIO,
            buffet_id=test_buffet.id,
        )

        assert par is None

    @pytest.mark.asyncio
    async def test_find_pair_filtra_por_buffet(self, db_session, test_buffet):
        """
        Test que filtra por buffet_id correctamente.
        """
        # Crear un CAV de otro buffet (sin buffet_id)
        cav_otro_buffet = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="cav_otro_buffet.pdf",
            storage_path="2024/01/cav_otro_buffet.pdf",
            tipo_documento=TipoDocumentoEnum.CAV,
            estado=EstadoDocumentoProcesadoEnum.ESPERANDO_PAR,
            buffet_id=None,  # Otro buffet (ninguno)
        )
        db_session.add(cav_otro_buffet)
        await db_session.flush()

        # Crear un OFICIO del buffet de test
        oficio = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="oficio_mi_buffet.pdf",
            storage_path="2024/01/oficio_mi_buffet.pdf",
            tipo_documento=TipoDocumentoEnum.OFICIO,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=test_buffet.id,
        )
        db_session.add(oficio)
        await db_session.flush()

        detector = DocumentPairDetector(db_session)
        par = await detector.find_pair(
            file_id=oficio.file_id,
            tipo_documento=TipoDocumentoEnum.OFICIO,
            buffet_id=test_buffet.id,
        )

        # No debe encontrar el CAV porque es de otro buffet
        assert par is None

    @pytest.mark.asyncio
    async def test_find_pair_retorna_candidato_cuando_hay_varios(self, db_session, test_buffet):
        """
        Test que retorna un candidato cuando hay varios disponibles.
        """
        # Crear múltiples CAVs pendientes
        cav1 = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="cav_1.pdf",
            storage_path="2024/01/cav_1.pdf",
            tipo_documento=TipoDocumentoEnum.CAV,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=test_buffet.id,
        )
        db_session.add(cav1)
        await db_session.flush()

        cav2 = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="cav_2.pdf",
            storage_path="2024/01/cav_2.pdf",
            tipo_documento=TipoDocumentoEnum.CAV,
            estado=EstadoDocumentoProcesadoEnum.ESPERANDO_PAR,
            buffet_id=test_buffet.id,
        )
        db_session.add(cav2)
        await db_session.flush()

        # Crear OFICIO
        oficio = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="oficio_multi.pdf",
            storage_path="2024/01/oficio_multi.pdf",
            tipo_documento=TipoDocumentoEnum.OFICIO,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=test_buffet.id,
        )
        db_session.add(oficio)
        await db_session.flush()

        detector = DocumentPairDetector(db_session)
        par = await detector.find_pair(
            file_id=oficio.file_id,
            tipo_documento=TipoDocumentoEnum.OFICIO,
            buffet_id=test_buffet.id,
        )

        assert par is not None
        # Debe retornar uno de los CAVs disponibles
        assert par.file_id in [cav1.file_id, cav2.file_id]
        assert par.tipo_documento == TipoDocumentoEnum.CAV

    @pytest.mark.asyncio
    async def test_find_pair_no_se_empareja_consigo_mismo(self, db_session, test_buffet):
        """
        Test que un documento no se empareja consigo mismo.
        """
        # Crear un único OFICIO
        oficio = DocumentoProcesadoModel(
            file_id=str(uuid.uuid4()).replace("-", ""),
            file_name="oficio_unico.pdf",
            storage_path="2024/01/oficio_unico.pdf",
            tipo_documento=TipoDocumentoEnum.OFICIO,
            estado=EstadoDocumentoProcesadoEnum.PENDIENTE,
            buffet_id=test_buffet.id,
        )
        db_session.add(oficio)
        await db_session.flush()

        detector = DocumentPairDetector(db_session)
        # Aunque busque tipo OFICIO (su propio tipo), no debe retornarse a sí mismo
        par = await detector.find_pair(
            file_id=oficio.file_id,
            tipo_documento=TipoDocumentoEnum.CAV,  # Busca CAV, no OFICIO
            buffet_id=test_buffet.id,
        )

        assert par is None
