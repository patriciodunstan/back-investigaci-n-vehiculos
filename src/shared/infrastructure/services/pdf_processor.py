"""
Procesador de PDFs para extracción de texto.

Extrae texto de archivos PDF usando PyPDF2/pdfplumber.
En el futuro se agregará soporte para OCR como fallback.

Principios aplicados:
- SRP: Solo maneja extracción de texto de PDFs
- OCP: Abierto para extensión (OCR en el futuro)
"""

import logging
from typing import BinaryIO, Optional
from io import BytesIO

try:
    import PyPDF2

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pytesseract
    from pdf2image import convert_from_bytes

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from src.core.config import get_settings


logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Procesador de PDFs para extracción de texto.

    Estrategia:
    1. Intentar extracción de texto nativo con PyPDF2
    2. Si falla o texto insuficiente, intentar con pdfplumber
    3. Si falla, usar OCR (pytesseract + pdf2image) como fallback

    Attributes:
        ocr_enabled: Si está habilitado el OCR
        ocr_language: Idioma para OCR (default: español)

    Example:
        >>> processor = PDFProcessor()
        >>> with open("documento.pdf", "rb") as f:
        ...     text = processor.extract_text(f)
    """

    def __init__(
        self,
        ocr_enabled: Optional[bool] = None,
        ocr_language: Optional[str] = None,
    ):
        """
        Inicializa el procesador de PDFs.

        Args:
            ocr_enabled: Si está habilitado el OCR (default: desde config)
            ocr_language: Idioma para OCR (default: desde config)
        """
        settings = get_settings()
        self.ocr_enabled = ocr_enabled if ocr_enabled is not None else settings.PDF_OCR_ENABLED
        self.ocr_language = ocr_language or settings.PDF_OCR_LANGUAGE

        if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            logger.warning(
                "Ni PyPDF2 ni pdfplumber están instalados. "
                "La extracción de texto puede no funcionar."
            )

        if self.ocr_enabled and not OCR_AVAILABLE:
            logger.warning(
                "OCR está habilitado pero pytesseract/pdf2image no están instalados. "
                "Instale: pip install pytesseract pdf2image pillow"
            )

    def extract_text(self, pdf_file: BinaryIO) -> str:
        """
        Extrae texto de un archivo PDF.

        Args:
            pdf_file: Archivo PDF como BinaryIO (debe estar al inicio)

        Returns:
            Texto extraído del PDF

        Raises:
            ValueError: Si el PDF está corrupto o no se puede leer
            RuntimeError: Si no hay librerías de PDF disponibles

        Example:
            >>> processor = PDFProcessor()
            >>> with open("documento.pdf", "rb") as f:
            ...     text = processor.extract_text(f)
        """
        # Asegurarse de que el archivo esté al inicio
        pdf_file.seek(0)

        # Intentar con PyPDF2 primero (más rápido)
        if PYPDF2_AVAILABLE:
            try:
                text = self._extract_with_pypdf2(pdf_file)
                if text and len(text.strip()) > 50:  # Mínimo de caracteres
                    logger.debug("Texto extraído exitosamente con PyPDF2")
                    return text
            except Exception as e:
                logger.warning(f"PyPDF2 falló: {str(e)}, intentando pdfplumber...")

        # Intentar con pdfplumber (más robusto)
        if PDFPLUMBER_AVAILABLE:
            try:
                pdf_file.seek(0)  # Resetear al inicio
                text = self._extract_with_pdfplumber(pdf_file)
                if text and len(text.strip()) > 50:
                    logger.debug("Texto extraído exitosamente con pdfplumber")
                    return text
            except Exception as e:
                logger.warning(f"pdfplumber falló: {str(e)}")

        # Si llegamos aquí, ambos métodos fallaron - intentar OCR si está habilitado
        if self.ocr_enabled and OCR_AVAILABLE:
            try:
                pdf_file.seek(0)  # Resetear al inicio
                text = self._extract_with_ocr(pdf_file)
                if text and len(text.strip()) > 50:
                    logger.info("Texto extraído exitosamente con OCR")
                    return text
            except Exception as e:
                logger.warning(f"OCR falló: {str(e)}")

        # Si llegamos aquí, todos los métodos fallaron
        if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            raise RuntimeError(
                "No hay librerías de PDF disponibles. "
                "Instale PyPDF2 o pdfplumber: pip install PyPDF2"
            )

        # Texto insuficiente o error
        logger.warning("No se pudo extraer texto suficiente del PDF con ningún método")
        return ""

    def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """
        Extrae texto de bytes de un PDF.

        Args:
            pdf_bytes: Bytes del archivo PDF

        Returns:
            Texto extraído del PDF

        Example:
            >>> processor = PDFProcessor()
            >>> with open("documento.pdf", "rb") as f:
            ...     pdf_bytes = f.read()
            >>> text = processor.extract_text_from_bytes(pdf_bytes)
        """
        pdf_file = BytesIO(pdf_bytes)
        return self.extract_text(pdf_file)

    def _extract_with_pypdf2(self, pdf_file: BinaryIO) -> str:
        """
        Extrae texto usando PyPDF2.

        Args:
            pdf_file: Archivo PDF como BinaryIO

        Returns:
            Texto extraído
        """
        pdf_file.seek(0)
        reader = PyPDF2.PdfReader(pdf_file)

        text_parts = []
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                logger.warning(f"Error extrayendo texto de página {page_num + 1}: {str(e)}")
                continue

        return "\n".join(text_parts)

    def _extract_with_pdfplumber(self, pdf_file: BinaryIO) -> str:
        """
        Extrae texto usando pdfplumber (más robusto que PyPDF2).

        Args:
            pdf_file: Archivo PDF como BinaryIO

        Returns:
            Texto extraído
        """
        pdf_file.seek(0)
        text_parts = []

        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Error extrayendo texto de página {page_num + 1}: {str(e)}")
                    continue

        return "\n".join(text_parts)

    def _extract_with_ocr(self, pdf_file: BinaryIO) -> str:
        """
        Extrae texto usando OCR (pytesseract + pdf2image).

        Convierte cada página del PDF a imagen y aplica OCR.
        Este método es más lento pero funciona con PDFs escaneados.

        Args:
            pdf_file: Archivo PDF como BinaryIO

        Returns:
            Texto extraído

        Raises:
            RuntimeError: Si OCR no está disponible
        """
        if not OCR_AVAILABLE:
            raise RuntimeError(
                "OCR no está disponible. " "Instale: pip install pytesseract pdf2image pillow"
            )

        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()

        # Convertir PDF a imágenes (una por página)
        try:
            images = convert_from_bytes(pdf_bytes, dpi=300)  # 300 DPI para mejor calidad
        except Exception as e:
            logger.error(f"Error convirtiendo PDF a imágenes: {str(e)}")
            raise

        text_parts = []
        for page_num, image in enumerate(images):
            try:
                # Aplicar OCR a la imagen
                page_text = pytesseract.image_to_string(
                    image,
                    lang=self.ocr_language,
                )
                if page_text:
                    text_parts.append(page_text)
                    logger.debug(
                        f"OCR extrajo {len(page_text)} caracteres de la página {page_num + 1}"
                    )
            except Exception as e:
                logger.warning(f"Error aplicando OCR a página {page_num + 1}: {str(e)}")
                continue

        return "\n".join(text_parts)

    def is_pdf(self, file_bytes: bytes) -> bool:
        """
        Verifica si los bytes corresponden a un archivo PDF.

        Args:
            file_bytes: Bytes del archivo (primeros bytes)

        Returns:
            True si parece ser un PDF
        """
        # PDFs empiezan con %PDF
        return file_bytes[:4] == b"%PDF"


# =============================================================================
# SINGLETON / DEPENDENCY INJECTION
# =============================================================================

_pdf_processor: Optional[PDFProcessor] = None


def get_pdf_processor() -> PDFProcessor:
    """
    Obtiene una instancia singleton del procesador de PDFs.

    Usar esta función para inyección de dependencias.

    Returns:
        PDFProcessor configurado

    Example:
        >>> from src.shared.infrastructure.services.pdf_processor import get_pdf_processor
        >>> processor = get_pdf_processor()
        >>> text = processor.extract_text_from_bytes(pdf_bytes)
    """
    global _pdf_processor
    if _pdf_processor is None:
        _pdf_processor = PDFProcessor()
    return _pdf_processor


def reset_pdf_processor() -> None:
    """Resetea el procesador singleton (útil para tests)."""
    global _pdf_processor
    _pdf_processor = None
