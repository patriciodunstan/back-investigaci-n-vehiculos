# Implementación Fase 1 y 2 - Google Drive Integration

Este documento contiene todo el código creado en las Fases 1 y 2 del plan de integración con Google Drive.

## Archivos Creados

### Fase 1: Infraestructura Base

#### 1. Google Drive API Client

**Ubicación:** `src/shared/infrastructure/external_apis/google_drive/`

**Archivos:**
- `client.py` - Cliente principal para Google Drive API
- `schemas.py` - Modelos Pydantic para respuestas
- `exceptions.py` - Excepciones personalizadas
- `__init__.py` - Exportaciones públicas

**Descripción:**
Cliente para interactuar con Google Drive API usando Service Account para autenticación. Proporciona métodos para descargar archivos, listar archivos en carpetas y obtener metadatos.

**Características:**
- Autenticación con Service Account (JSON o path a archivo)
- Métodos async usando httpx
- Manejo de errores con excepciones específicas
- Soporte para paginación en listado de archivos
- Descarga de archivos como bytes o stream

#### 2. PDF Processor

**Ubicación:** `src/shared/infrastructure/services/pdf_processor.py`

**Descripción:**
Procesador de PDFs para extracción de texto. Utiliza PyPDF2 y pdfplumber como estrategia de fallback. En el futuro se agregará soporte para OCR (Fase 5).

**Características:**
- Extracción de texto nativo de PDFs
- Fallback entre PyPDF2 y pdfplumber
- Soporte para archivos BinaryIO y bytes
- Validación de formato PDF

---

## Código de los Archivos

### `src/shared/infrastructure/external_apis/google_drive/exceptions.py`

```python
"""
Excepciones personalizadas para la API de Google Drive.

Define errores específicos para manejar diferentes situaciones
de la integración con Google Drive API.
"""


class GoogleDriveAPIError(Exception):
    """
    Error base para todas las excepciones de Google Drive.
    
    Attributes:
        message: Mensaje descriptivo del error
        status_code: Código HTTP de la respuesta (si aplica)
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: int = None
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"HTTP: {self.status_code}")
        return " | ".join(parts)


class GoogleDriveAuthenticationError(GoogleDriveAPIError):
    """
    Error de autenticación con Google Drive API.
    
    Se produce cuando:
    - Service Account JSON inválido o expirado
    - Permisos insuficientes
    - Credenciales no configuradas
    """
    
    def __init__(self, message: str = "Error de autenticación con Google Drive API"):
        super().__init__(message, status_code=401)


class GoogleDriveNotFoundError(GoogleDriveAPIError):
    """
    Error cuando no se encuentra el recurso solicitado.
    
    Ejemplos:
    - Archivo no existe
    - Carpeta no existe
    """
    
    def __init__(self, message: str = "Recurso no encontrado en Google Drive"):
        super().__init__(message, status_code=404)


class GoogleDrivePermissionError(GoogleDriveAPIError):
    """
    Error de permisos insuficientes.
    
    Se produce cuando:
    - No se tiene acceso al archivo/carpeta
    - Service Account no tiene permisos compartidos
    """
    
    def __init__(self, message: str = "Permisos insuficientes para acceder al recurso"):
        super().__init__(message, status_code=403)


class GoogleDriveQuotaExceededError(GoogleDriveAPIError):
    """
    Error cuando se excede la cuota de la API.
    
    Google Drive tiene límites de requests por día.
    """
    
    def __init__(self, message: str = "Cuota de Google Drive API excedida"):
        super().__init__(message, status_code=429)


class GoogleDriveTimeoutError(GoogleDriveAPIError):
    """
    Error por timeout en la conexión con Google Drive.
    """
    
    def __init__(self, message: str = "Timeout al conectar con Google Drive API"):
        super().__init__(message, status_code=408)
```

### `src/shared/infrastructure/external_apis/google_drive/schemas.py`

```python
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
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DriveFileListResponse(BaseModel):
    """
    Respuesta de listado de archivos de Google Drive.
    
    Attributes:
        files: Lista de archivos
        next_page_token: Token para la siguiente página (si hay más resultados)
    """
    
    files: List[DriveFileMetadata] = Field(default_factory=list, description="Lista de archivos")
    next_page_token: Optional[str] = Field(None, description="Token para siguiente página")
```

### `src/shared/infrastructure/external_apis/google_drive/client.py`

Ver código completo en: `src/shared/infrastructure/external_apis/google_drive/client.py`

**Resumen:**
- Clase `GoogleDriveClient` con métodos async
- Autenticación con Service Account
- Métodos: `get_file_metadata()`, `list_files()`, `download_file()`, `download_file_as_stream()`
- Singleton pattern con `get_google_drive_client()`

### `src/shared/infrastructure/external_apis/google_drive/__init__.py`

```python
"""
Google Drive API Client.

Cliente para integración con Google Drive API usando Service Account.
https://developers.google.com/drive/api

Servicios disponibles:
- Descargar archivos desde Google Drive
- Listar archivos en carpetas
- Obtener metadatos de archivos
"""

from .client import GoogleDriveClient, get_google_drive_client, reset_google_drive_client
from .schemas import DriveFileMetadata, DriveFileListResponse
from .exceptions import (
    GoogleDriveAPIError,
    GoogleDriveAuthenticationError,
    GoogleDriveNotFoundError,
    GoogleDrivePermissionError,
    GoogleDriveQuotaExceededError,
    GoogleDriveTimeoutError,
)

__all__ = [
    "GoogleDriveClient",
    "get_google_drive_client",
    "reset_google_drive_client",
    "DriveFileMetadata",
    "DriveFileListResponse",
    "GoogleDriveAPIError",
    "GoogleDriveAuthenticationError",
    "GoogleDriveNotFoundError",
    "GoogleDrivePermissionError",
    "GoogleDriveQuotaExceededError",
    "GoogleDriveTimeoutError",
]
```

### `src/shared/infrastructure/services/pdf_processor.py`

Ver código completo en: `src/shared/infrastructure/services/pdf_processor.py`

**Resumen:**
- Clase `PDFProcessor` para extracción de texto
- Soporte para PyPDF2 y pdfplumber (fallback)
- Métodos: `extract_text()`, `extract_text_from_bytes()`, `is_pdf()`
- Singleton pattern con `get_pdf_processor()`

---

## Dependencias Requeridas

Para usar estos componentes, se necesitan las siguientes librerías:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install PyPDF2 pdfplumber
```

**Nota:** Estas dependencias deben agregarse a `requirements.txt` o `pyproject.toml` del proyecto.

---

## Configuración Necesaria

### Variables de Entorno

Ya agregadas en `src/core/config.py`:

- `GOOGLE_DRIVE_ENABLED`: Habilitar/deshabilitar integración
- `GOOGLE_DRIVE_FOLDER_ID`: ID de carpeta raíz a monitorear
- `GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON`: JSON de Service Account (string o path)
- `GOOGLE_DRIVE_WEBHOOK_SECRET`: Secreto para validar webhooks
- `GOOGLE_DRIVE_DOMAIN_WHITELIST`: Dominios permitidos
- `PDF_OCR_ENABLED`: Habilitar OCR (futuro)
- `PDF_OCR_LANGUAGE`: Idioma para OCR (default: "spa")
- `PDF_MAX_SIZE_MB`: Tamaño máximo de PDF
- `PDF_PROCESSING_TIMEOUT_SECONDS`: Timeout para procesamiento

---

## Próximos Pasos

1. **Fase 2 - Parsers:**
   - Crear `OficioParser` para extraer datos de oficios
   - Crear `CAVParser` para extraer datos de certificados CAV
   - Crear `DocumentPairDetector` para identificar pares de documentos
   - Crear `BuffetMapper` para mapear carpetas a buffets

2. **Testing:**
   - Agregar tests unitarios para GoogleDriveClient
   - Agregar tests unitarios para PDFProcessor
   - Agregar tests de integración

3. **Documentación:**
   - Agregar ejemplos de uso
   - Documentar configuración de Service Account
   - Agregar diagramas de flujo

---

## Notas de Implementación

- El cliente de Google Drive usa `httpx` para requests async, pero `google-auth` para autenticación (sync). Esto es aceptable ya que la autenticación es poco frecuente.
- El PDFProcessor intenta PyPDF2 primero (más rápido) y luego pdfplumber (más robusto).
- OCR se implementará en la Fase 5 como fallback cuando la extracción de texto nativo falle.
