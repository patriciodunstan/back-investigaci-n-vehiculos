"""
Tests de integración para endpoint de subida de documentos.

Verifica el flujo completo de subida y procesamiento de documentos.
"""

import pytest
import io
from fastapi import status
from unittest.mock import MagicMock, patch, AsyncMock


class TestDocumentUploadEndpoint:
    """Tests para endpoint POST /oficios/documents/upload-batch."""

    @pytest.mark.asyncio
    async def test_upload_batch_exitoso(
        self, test_client, auth_headers, test_buffet, mock_pdf_bytes
    ):
        """
        Test subida exitosa de documentos PDF.
        """
        # Mock del storage y pdf processor
        mock_storage = MagicMock()
        mock_storage.save_file.return_value = "2024/01/test.pdf"

        mock_pdf_processor = MagicMock()
        mock_pdf_processor.extract_text_from_bytes.return_value = "OFICIO N° 1234"

        with patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_file_storage",
            return_value=mock_storage,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_pdf_processor",
            return_value=mock_pdf_processor,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router._process_document_in_background",
            new_callable=AsyncMock,
        ):
            # Crear archivo de test
            files = [
                ("files", ("oficio_test.pdf", io.BytesIO(mock_pdf_bytes), "application/pdf")),
            ]

            response = await test_client.post(
                "/oficios/documents/upload-batch",
                headers=auth_headers,
                files=files,
                data={"buffet_id": str(test_buffet.id)},
            )

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["status"] == "accepted"
            assert data["total_files"] == 1
            assert len(data["processed_files"]) == 1
            assert data["processed_files"][0]["status"] == "processing"

    @pytest.mark.asyncio
    async def test_upload_batch_multiples_archivos(
        self, test_client, auth_headers, test_buffet, mock_pdf_bytes
    ):
        """
        Test subida de múltiples archivos PDF.
        """
        mock_storage = MagicMock()
        mock_storage.save_file.return_value = "2024/01/test.pdf"

        mock_pdf_processor = MagicMock()
        mock_pdf_processor.extract_text_from_bytes.side_effect = [
            "OFICIO N° 1234",  # Primer archivo -> OFICIO
            "CERTIFICADO DE INSCRIPCIÓN Patente ABCD12",  # Segundo archivo -> CAV
        ]

        with patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_file_storage",
            return_value=mock_storage,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_pdf_processor",
            return_value=mock_pdf_processor,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router._process_document_in_background",
            new_callable=AsyncMock,
        ):
            files = [
                ("files", ("oficio.pdf", io.BytesIO(mock_pdf_bytes), "application/pdf")),
                ("files", ("cav.pdf", io.BytesIO(mock_pdf_bytes), "application/pdf")),
            ]

            response = await test_client.post(
                "/oficios/documents/upload-batch",
                headers=auth_headers,
                files=files,
                data={"buffet_id": str(test_buffet.id)},
            )

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["total_files"] == 2
            assert len(data["processed_files"]) == 2

    @pytest.mark.asyncio
    async def test_upload_batch_rechaza_archivo_no_pdf(
        self, test_client, auth_headers, test_buffet
    ):
        """
        Test que rechaza archivos que no son PDF.
        """
        mock_storage = MagicMock()
        mock_pdf_processor = MagicMock()

        with patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_file_storage",
            return_value=mock_storage,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_pdf_processor",
            return_value=mock_pdf_processor,
        ):
            # Archivo que no es PDF (contenido no empieza con %PDF)
            files = [
                ("files", ("documento.pdf", io.BytesIO(b"esto no es pdf"), "application/pdf")),
            ]

            response = await test_client.post(
                "/oficios/documents/upload-batch",
                headers=auth_headers,
                files=files,
                data={"buffet_id": str(test_buffet.id)},
            )

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            # El archivo se marca como error
            assert data["processed_files"][0]["status"] == "error"

    @pytest.mark.asyncio
    async def test_upload_batch_rechaza_tipo_incorrecto(
        self, test_client, auth_headers, test_buffet
    ):
        """
        Test que rechaza archivos con content-type incorrecto.
        """
        mock_storage = MagicMock()
        mock_pdf_processor = MagicMock()

        with patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_file_storage",
            return_value=mock_storage,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_pdf_processor",
            return_value=mock_pdf_processor,
        ):
            files = [
                ("files", ("imagen.jpg", io.BytesIO(b"fake image"), "image/jpeg")),
            ]

            response = await test_client.post(
                "/oficios/documents/upload-batch",
                headers=auth_headers,
                files=files,
                data={"buffet_id": str(test_buffet.id)},
            )

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["processed_files"][0]["status"] == "error"

    @pytest.mark.asyncio
    async def test_upload_batch_sin_archivos_falla(
        self, test_client, auth_headers, test_buffet
    ):
        """
        Test que falla cuando no se envían archivos.
        """
        response = await test_client.post(
            "/oficios/documents/upload-batch",
            headers=auth_headers,
            data={"buffet_id": str(test_buffet.id)},
        )

        # FastAPI valida que files es requerido
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    @pytest.mark.asyncio
    async def test_upload_batch_requiere_autenticacion(self, test_client, mock_pdf_bytes):
        """
        Test que requiere autenticación.
        """
        files = [
            ("files", ("oficio.pdf", io.BytesIO(mock_pdf_bytes), "application/pdf")),
        ]

        response = await test_client.post(
            "/oficios/documents/upload-batch",
            files=files,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_upload_batch_detecta_tipo_oficio(
        self, test_client, auth_headers, test_buffet, mock_pdf_bytes
    ):
        """
        Test que detecta correctamente tipo OFICIO por nombre de archivo.
        """
        mock_storage = MagicMock()
        mock_storage.save_file.return_value = "2024/01/oficio.pdf"

        mock_pdf_processor = MagicMock()
        mock_pdf_processor.extract_text_from_bytes.return_value = "texto generico"

        with patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_file_storage",
            return_value=mock_storage,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_pdf_processor",
            return_value=mock_pdf_processor,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router._process_document_in_background",
            new_callable=AsyncMock,
        ):
            # Usar nombre de archivo con keyword "oficio" para detección
            files = [
                ("files", ("oficio_1234.pdf", io.BytesIO(mock_pdf_bytes), "application/pdf")),
            ]

            response = await test_client.post(
                "/oficios/documents/upload-batch",
                headers=auth_headers,
                files=files,
            )

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["processed_files"][0]["tipo_documento"] == "oficio"

    @pytest.mark.asyncio
    async def test_upload_batch_detecta_tipo_cav(
        self, test_client, auth_headers, test_buffet, mock_pdf_bytes
    ):
        """
        Test que detecta correctamente tipo CAV por nombre de archivo.
        """
        mock_storage = MagicMock()
        mock_storage.save_file.return_value = "2024/01/cav.pdf"

        mock_pdf_processor = MagicMock()
        mock_pdf_processor.extract_text_from_bytes.return_value = "texto generico"

        with patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_file_storage",
            return_value=mock_storage,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_pdf_processor",
            return_value=mock_pdf_processor,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router._process_document_in_background",
            new_callable=AsyncMock,
        ):
            # Usar nombre de archivo con keyword "cav" para detección
            files = [
                ("files", ("CAV_vehiculo.pdf", io.BytesIO(mock_pdf_bytes), "application/pdf")),
            ]

            response = await test_client.post(
                "/oficios/documents/upload-batch",
                headers=auth_headers,
                files=files,
            )

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["processed_files"][0]["tipo_documento"] == "cav"

    @pytest.mark.asyncio
    async def test_upload_batch_genera_file_id_unico(
        self, test_client, auth_headers, test_buffet, mock_pdf_bytes
    ):
        """
        Test que genera file_id único para cada archivo.
        """
        mock_storage = MagicMock()
        mock_storage.save_file.return_value = "2024/01/test.pdf"

        mock_pdf_processor = MagicMock()
        mock_pdf_processor.extract_text_from_bytes.return_value = "OFICIO"

        with patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_file_storage",
            return_value=mock_storage,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router.get_pdf_processor",
            return_value=mock_pdf_processor,
        ), patch(
            "src.modules.oficios.presentation.routers.document_upload_router._process_document_in_background",
            new_callable=AsyncMock,
        ):
            files = [
                ("files", ("doc1.pdf", io.BytesIO(mock_pdf_bytes), "application/pdf")),
                ("files", ("doc2.pdf", io.BytesIO(mock_pdf_bytes), "application/pdf")),
            ]

            response = await test_client.post(
                "/oficios/documents/upload-batch",
                headers=auth_headers,
                files=files,
            )

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()

            file_ids = [f["file_id"] for f in data["processed_files"]]
            # Todos los file_id deben ser únicos
            assert len(file_ids) == len(set(file_ids))
            # Todos deben tener valor
            assert all(fid for fid in file_ids)
