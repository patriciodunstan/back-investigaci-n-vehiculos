"""
Tests unitarios para CreateOficioFromDocumentPairUseCase.

Verifica la creación de oficios desde pares de documentos con enriquecimiento Boostr.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.modules.oficios.application.dtos import (
    OficioExtraidoDTO,
    CAVExtraidoDTO,
    ParDocumentoDTO,
)


class TestCreateOficioFromDocumentPairUseCase:
    """Tests para CreateOficioFromDocumentPairUseCase."""

    @pytest.fixture
    def oficio_extraido_valido(self) -> OficioExtraidoDTO:
        """Fixture para datos de oficio extraídos válidos."""
        return OficioExtraidoDTO(
            numero_oficio="TEST-2024-001",
            rut_propietario="12.345.678-9",
            nombre_propietario="Juan Carlos Pérez",
            direcciones=["Av. Providencia 1234, Santiago"],
            contexto_legal="Causa ROL C-5678-2024",
        )

    @pytest.fixture
    def cav_extraido_valido(self) -> CAVExtraidoDTO:
        """Fixture para datos de CAV extraídos válidos."""
        return CAVExtraidoDTO(
            patente="ABCD12",
            marca="TOYOTA",
            modelo="COROLLA",
            año=2020,
            color="BLANCO",
            vin="JTDKARFH8J5087562",
            tipo="AUTOMÓVIL",
            combustible="BENCINA",
        )

    @pytest.fixture
    def par_documento_valido(
        self, oficio_extraido_valido, cav_extraido_valido
    ) -> ParDocumentoDTO:
        """Fixture para par de documentos válido."""
        return ParDocumentoDTO(
            file_id_oficio="abc123",
            file_id_cav="def456",
            file_name_oficio="oficio.pdf",
            file_name_cav="cav.pdf",
            storage_path_oficio="2024/01/oficio.pdf",
            storage_path_cav="2024/01/cav.pdf",
            oficio_extraido=oficio_extraido_valido,
            cav_extraido=cav_extraido_valido,
            buffet_id=1,
            pdf_bytes_oficio=b"%PDF-test-oficio",
            pdf_bytes_cav=b"%PDF-test-cav",
        )

    @pytest.mark.asyncio
    async def test_execute_crea_oficio_exitosamente(
        self, db_session, par_documento_valido, test_buffet
    ):
        """
        Test que crea un oficio exitosamente desde un par de documentos.
        """
        from src.modules.oficios.application.use_cases import (
            CreateOficioFromDocumentPairUseCase,
        )
        from src.modules.oficios.infrastructure.repositories import OficioRepository

        # Actualizar buffet_id con el de test
        par_dto = ParDocumentoDTO(
            file_id_oficio=par_documento_valido.file_id_oficio,
            file_id_cav=par_documento_valido.file_id_cav,
            file_name_oficio=par_documento_valido.file_name_oficio,
            file_name_cav=par_documento_valido.file_name_cav,
            storage_path_oficio=par_documento_valido.storage_path_oficio,
            storage_path_cav=par_documento_valido.storage_path_cav,
            oficio_extraido=par_documento_valido.oficio_extraido,
            cav_extraido=par_documento_valido.cav_extraido,
            buffet_id=test_buffet.id,
            pdf_bytes_oficio=par_documento_valido.pdf_bytes_oficio,
            pdf_bytes_cav=par_documento_valido.pdf_bytes_cav,
        )

        repository = OficioRepository(db_session)

        # Mock del cliente Boostr para que no haga llamadas reales
        mock_boostr = AsyncMock()
        mock_boostr.check_deceased.return_value = MagicMock(
            fallecido=False, fecha_defuncion=None
        )
        mock_boostr.get_person_properties.return_value = []

        with patch(
            "src.modules.oficios.application.use_cases.create_oficio_from_document_pair.get_boostr_client",
            return_value=mock_boostr,
        ):
            use_case = CreateOficioFromDocumentPairUseCase(repository)
            result = await use_case.execute(par_dto)

            assert result is not None
            assert result.numero_oficio == "TEST-2024-001"
            assert len(result.vehiculos) == 1
            assert result.vehiculos[0].patente == "ABCD12"

    @pytest.mark.asyncio
    async def test_execute_falla_sin_numero_oficio(self, db_session, test_buffet):
        """
        Test que falla cuando no hay número de oficio.
        """
        from src.modules.oficios.application.use_cases import (
            CreateOficioFromDocumentPairUseCase,
        )
        from src.modules.oficios.infrastructure.repositories import OficioRepository

        # Crear par sin número de oficio
        par_dto = ParDocumentoDTO(
            file_id_oficio="abc123",
            file_id_cav="def456",
            file_name_oficio="oficio.pdf",
            file_name_cav="cav.pdf",
            storage_path_oficio="2024/01/oficio.pdf",
            storage_path_cav="2024/01/cav.pdf",
            oficio_extraido=OficioExtraidoDTO(
                numero_oficio=None,  # Sin número
                rut_propietario="12.345.678-9",
                nombre_propietario="Juan Pérez",
            ),
            cav_extraido=CAVExtraidoDTO(patente="ABCD12"),
            buffet_id=test_buffet.id,
        )

        repository = OficioRepository(db_session)

        mock_boostr = AsyncMock()
        mock_boostr.check_deceased.return_value = MagicMock(fallecido=False)
        mock_boostr.get_person_properties.return_value = []

        with patch(
            "src.modules.oficios.application.use_cases.create_oficio_from_document_pair.get_boostr_client",
            return_value=mock_boostr,
        ):
            use_case = CreateOficioFromDocumentPairUseCase(repository)

            with pytest.raises(ValueError) as exc_info:
                await use_case.execute(par_dto)

            assert "número de oficio" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_execute_falla_sin_patente(self, db_session, test_buffet):
        """
        Test que falla cuando no hay patente en el CAV.
        """
        from src.modules.oficios.application.use_cases import (
            CreateOficioFromDocumentPairUseCase,
        )
        from src.modules.oficios.infrastructure.repositories import OficioRepository

        # Crear par sin patente
        par_dto = ParDocumentoDTO(
            file_id_oficio="abc123",
            file_id_cav="def456",
            file_name_oficio="oficio.pdf",
            file_name_cav="cav.pdf",
            storage_path_oficio="2024/01/oficio.pdf",
            storage_path_cav="2024/01/cav.pdf",
            oficio_extraido=OficioExtraidoDTO(
                numero_oficio="TEST-001",
                rut_propietario="12.345.678-9",
                nombre_propietario="Juan Pérez",
            ),
            cav_extraido=CAVExtraidoDTO(patente=None),  # Sin patente
            buffet_id=test_buffet.id,
        )

        repository = OficioRepository(db_session)

        mock_boostr = AsyncMock()
        mock_boostr.check_deceased.return_value = MagicMock(fallecido=False)
        mock_boostr.get_person_properties.return_value = []

        with patch(
            "src.modules.oficios.application.use_cases.create_oficio_from_document_pair.get_boostr_client",
            return_value=mock_boostr,
        ):
            use_case = CreateOficioFromDocumentPairUseCase(repository)

            with pytest.raises(ValueError) as exc_info:
                await use_case.execute(par_dto)

            assert "patente" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_execute_enriquece_con_boostr_propiedades(
        self, db_session, test_buffet
    ):
        """
        Test que enriquece con propiedades de Boostr.
        """
        from src.modules.oficios.application.use_cases import (
            CreateOficioFromDocumentPairUseCase,
        )
        from src.modules.oficios.infrastructure.repositories import OficioRepository

        par_dto = ParDocumentoDTO(
            file_id_oficio="abc123",
            file_id_cav="def456",
            file_name_oficio="oficio.pdf",
            file_name_cav="cav.pdf",
            storage_path_oficio="2024/01/oficio.pdf",
            storage_path_cav="2024/01/cav.pdf",
            oficio_extraido=OficioExtraidoDTO(
                numero_oficio="TEST-BOOSTR-001",
                rut_propietario="12.345.678-9",
                nombre_propietario="Juan Pérez",
                direcciones=["Av. Principal 100"],
            ),
            cav_extraido=CAVExtraidoDTO(
                patente="BOOSTR01",
                marca="TOYOTA",
            ),
            buffet_id=test_buffet.id,
        )

        repository = OficioRepository(db_session)

        # Mock Boostr con propiedades
        mock_property = MagicMock()
        mock_property.rol = "1-23-456"
        mock_property.comuna = "Santiago"
        mock_property.direccion = "Av. Boostr 200"
        mock_property.destino = "Habitacional"
        mock_property.avaluo = 150000000

        mock_boostr = AsyncMock()
        mock_boostr.check_deceased.return_value = MagicMock(fallecido=False)
        mock_boostr.get_person_properties.return_value = [mock_property]

        with patch(
            "src.modules.oficios.application.use_cases.create_oficio_from_document_pair.get_boostr_client",
            return_value=mock_boostr,
        ):
            use_case = CreateOficioFromDocumentPairUseCase(repository)
            result = await use_case.execute(par_dto)

            # Verificar que se consultó Boostr
            mock_boostr.check_deceased.assert_called_once()
            mock_boostr.get_person_properties.assert_called_once()

            # Debe haber direcciones (del oficio + de Boostr)
            assert len(result.direcciones) >= 1

    @pytest.mark.asyncio
    async def test_execute_marca_propietario_fallecido(self, db_session, test_buffet):
        """
        Test que marca al propietario como fallecido si Boostr lo indica.
        """
        from src.modules.oficios.application.use_cases import (
            CreateOficioFromDocumentPairUseCase,
        )
        from src.modules.oficios.infrastructure.repositories import OficioRepository

        par_dto = ParDocumentoDTO(
            file_id_oficio="abc123",
            file_id_cav="def456",
            file_name_oficio="oficio.pdf",
            file_name_cav="cav.pdf",
            storage_path_oficio="2024/01/oficio.pdf",
            storage_path_cav="2024/01/cav.pdf",
            oficio_extraido=OficioExtraidoDTO(
                numero_oficio="TEST-FALLECIDO-001",
                rut_propietario="12.345.678-9",
                nombre_propietario="Juan Pérez Fallecido",
                direcciones=["Av. Test 100"],
            ),
            cav_extraido=CAVExtraidoDTO(
                patente="FALLEC01",
                marca="TOYOTA",
            ),
            buffet_id=test_buffet.id,
        )

        repository = OficioRepository(db_session)

        # Mock Boostr indicando fallecido
        mock_boostr = AsyncMock()
        mock_boostr.check_deceased.return_value = MagicMock(
            fallecido=True, fecha_defuncion="2023-06-15"
        )
        mock_boostr.get_person_properties.return_value = []

        with patch(
            "src.modules.oficios.application.use_cases.create_oficio_from_document_pair.get_boostr_client",
            return_value=mock_boostr,
        ):
            use_case = CreateOficioFromDocumentPairUseCase(repository)
            result = await use_case.execute(par_dto)

            # Verificar que el propietario tiene nota de fallecido
            assert len(result.propietarios) >= 1
            propietario = result.propietarios[0]
            assert propietario.notas is not None
            assert "FALLECIDO" in propietario.notas.upper()

    @pytest.mark.asyncio
    async def test_execute_continua_si_boostr_falla(self, db_session, test_buffet):
        """
        Test que continúa creando el oficio aunque Boostr falle.
        """
        from src.modules.oficios.application.use_cases import (
            CreateOficioFromDocumentPairUseCase,
        )
        from src.modules.oficios.infrastructure.repositories import OficioRepository
        from src.shared.infrastructure.external_apis.boostr.exceptions import (
            BoostrAPIError,
        )

        par_dto = ParDocumentoDTO(
            file_id_oficio="abc123",
            file_id_cav="def456",
            file_name_oficio="oficio.pdf",
            file_name_cav="cav.pdf",
            storage_path_oficio="2024/01/oficio.pdf",
            storage_path_cav="2024/01/cav.pdf",
            oficio_extraido=OficioExtraidoDTO(
                numero_oficio="TEST-BOOSTR-ERROR-001",
                rut_propietario="12.345.678-9",
                nombre_propietario="Juan Pérez",
                direcciones=["Av. Test 100"],
            ),
            cav_extraido=CAVExtraidoDTO(
                patente="BOOERR01",
                marca="TOYOTA",
            ),
            buffet_id=test_buffet.id,
        )

        repository = OficioRepository(db_session)

        # Mock Boostr que falla
        mock_boostr = AsyncMock()
        mock_boostr.check_deceased.side_effect = BoostrAPIError("API no disponible")
        mock_boostr.get_person_properties.side_effect = BoostrAPIError("API no disponible")

        with patch(
            "src.modules.oficios.application.use_cases.create_oficio_from_document_pair.get_boostr_client",
            return_value=mock_boostr,
        ):
            use_case = CreateOficioFromDocumentPairUseCase(repository)

            # No debe fallar, debe crear el oficio sin enriquecimiento
            result = await use_case.execute(par_dto)

            assert result is not None
            assert result.numero_oficio == "TEST-BOOSTR-ERROR-001"
