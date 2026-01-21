"""
Servicios compartidos de infraestructura.

Proporciona servicios reutilizables como procesamiento de PDFs,
almacenamiento de archivos, etc.
"""

from src.shared.infrastructure.services.file_storage import (
    FileStorageService,
    get_file_storage,
)
from src.shared.infrastructure.services.pdf_processor import (
    PDFProcessor,
    get_pdf_processor,
)

__all__ = [
    "FileStorageService",
    "get_file_storage",
    "PDFProcessor",
    "get_pdf_processor",
]
