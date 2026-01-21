"""
Esquemas de datos para respuestas de la API de Google Drive.

Define modelos Pydantic para parsear y validar las respuestas
de los diferentes endpoints de Google Drive API.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class DriveFileMetadata(BaseModel):
    """
    Metadatos de un archivo en Google Drive.

    Attributes:
        id: ID único del archivo
        name: Nombre del archivo
        mime_type: Tipo MIME del archivo
        size: Tamaño en bytes
        created_time: Fecha de creación
        modified_time: Fecha de última modificación
        parents: Lista de IDs de carpetas padre
        web_view_link: URL para ver el archivo en el navegador
        web_content_link: URL para descargar el archivo
    """

    id: str = Field(..., description="ID único del archivo")
    name: str = Field(..., description="Nombre del archivo")
    mime_type: Optional[str] = Field(None, description="Tipo MIME del archivo")
    size: Optional[str] = Field(None, description="Tamaño en bytes (como string)")
    created_time: Optional[datetime] = Field(None, description="Fecha de creación")
    modified_time: Optional[datetime] = Field(None, description="Fecha de última modificación")
    parents: Optional[List[str]] = Field(None, description="IDs de carpetas padre")
    web_view_link: Optional[str] = Field(None, description="URL para ver en navegador")
    web_content_link: Optional[str] = Field(None, description="URL para descargar")

    @property
    def size_bytes(self) -> Optional[int]:
        """Retorna el tamaño en bytes como entero."""
        if self.size:
            try:
                return int(self.size)
            except (ValueError, TypeError):
                return None
        return None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class DriveFileListResponse(BaseModel):
    """
    Respuesta de listado de archivos de Google Drive.

    Attributes:
        files: Lista de archivos
        next_page_token: Token para la siguiente página (si hay más resultados)
    """

    files: List[DriveFileMetadata] = Field(default_factory=list, description="Lista de archivos")
    next_page_token: Optional[str] = Field(None, description="Token para siguiente página")
