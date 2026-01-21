# Plan: Creación Automática de Oficios desde Google Drive

## Objetivo

Implementar un sistema completo que detecte automáticamente pares de documentos PDF (Oficio + CAV) subidos a Google Drive, extraiga información estructurada de cada tipo de documento, combine los datos de ambos, enriquezca la información consultando la API de Boostr, y cree oficios automáticamente con vehículos, propietarios y direcciones.

## Arquitectura General

El sistema procesa pares de documentos:
- **Oficio**: Contiene información del caso (número de oficio, propietario, direcciones, contexto legal)
- **CAV (Certificado de Inscripción y Anotaciones Vigentes)**: Contiene información del vehículo (patente, marca, modelo, año, color, VIN)

El flujo completo:
1. **Detección**: Webhook de Google Drive detecta nuevos PDFs
2. **Emparejamiento**: Sistema identifica pares de documentos (Oficio + CAV)
3. **Extracción**: Cada documento se parsea con su parser específico
4. **Combinación**: Información de ambos documentos se combina inteligentemente
5. **Enriquecimiento**: Consulta a Boostr API para datos adicionales
6. **Creación**: Se crea el oficio completo con todos los datos
7. **Adjuntos**: Ambos PDFs se guardan como adjuntos del oficio

## Componentes del Sistema

### 1. Google Drive API Client

**Ubicación:** `src/shared/infrastructure/external_apis/google_drive/`

**Archivos:**
- `__init__.py`: Exportaciones públicas
- `client.py`: Cliente HTTP con autenticación Service Account
- `schemas.py`: Modelos Pydantic para respuestas de Google Drive API
- `exceptions.py`: Excepciones específicas (GoogleDriveAPIError, etc.)

**Responsabilidades:**
- Autenticación con Service Account (JSON key)
- Descarga de archivos PDF desde Google Drive
- Listado de archivos en una carpeta
- Obtener metadatos de archivos (nombre, fecha, tamaño, etc.)
- Singleton pattern para reutilizar conexiones

**Configuración requerida:**
- Service Account JSON (variable de entorno o archivo)
- Folder ID de Google Drive a monitorear
- Permisos de lectura en la carpeta compartida

### 2. PDF Processor

**Ubicación:** `src/shared/infrastructure/services/pdf_processor.py`

**Responsabilidades:**
- Extracción de texto de PDFs usando PyPDF2 o pdfplumber
- Fallback a OCR (pytesseract + pdf2image) si el PDF es escaneado
- Manejo de errores (PDF corrupto, protegido, etc.)
- Retornar texto plano para parsing

**Estrategia:**
1. Intentar extracción de texto nativo
2. Si falla o texto insuficiente, convertir a imágenes
3. Aplicar OCR con pytesseract
4. Retornar texto combinado

### 3. OficioParser

**Ubicación:** `src/modules/oficios/infrastructure/services/oficio_parser.py`

**Responsabilidades:**
- Parsear texto extraído de documentos de tipo "Oficio"
- Extraer información específica usando regex patterns

**Datos a extraer:**
- Número de oficio (patrones: "OF-2024-001", "ROL-12345", etc.)
- RUT del propietario (formato chileno)
- Nombre completo del propietario
- Direcciones (múltiples líneas con comuna/región)
- Contexto legal o motivo del oficio
- Fecha del oficio

**Estrategia de parsing:**
- Regex patterns específicos para cada campo
- Validación de formatos (RUT, número de oficio)
- Limpieza de texto (normalización, espacios)
- Manejo de variaciones de formato

### 4. CAVParser

**Ubicación:** `src/modules/oficios/infrastructure/services/cav_parser.py`

**Responsabilidades:**
- Parsear texto extraído de documentos de tipo "CAV"
- Extraer información específica del certificado

**Datos a extraer:**
- Patente del vehículo
- Marca
- Modelo
- Año
- Color
- VIN (Número de chasis)
- Tipo de vehículo
- Combustible

**Estrategia de parsing:**
- Regex patterns específicos para campos del CAV
- Búsqueda de secciones específicas del documento
- Validación de formato de patente chilena
- Normalización de valores (colores, marcas)

### 5. DocumentPairDetector

**Ubicación:** `src/modules/oficios/infrastructure/services/document_pair_detector.py`

**Responsabilidades:**
- Identificar si un PDF nuevo tiene un par (Oficio o CAV)
- Buscar documentos relacionados en la misma carpeta
- Establecer relaciones entre pares de documentos

**Estrategias de matching:**
1. **Por nombre de archivo**: Buscar patrones similares
2. **Por fecha**: Archivos subidos en el mismo día/rango
3. **Por contenido**: Si ya se procesó uno, buscar por número de oficio o patente
4. **Por ubicación**: Misma carpeta de Google Drive

**Lógica:**
- Cuando llega un PDF nuevo, buscar en `documentos_procesados` por:
  - Misma carpeta (`drive_folder_id`)
  - Estado `ESPERANDO_PAR`
  - Fecha similar (dentro de X horas)
- Si encuentra match, establecer `par_documento_id` en ambos registros

### 6. BuffetMapper

**Ubicación:** `src/modules/oficios/infrastructure/services/buffet_mapper.py`

**Responsabilidades:**
- Mapear carpetas de Google Drive a `buffet_id`
- Configuración flexible (archivo JSON, base de datos, o variable de entorno)

**Estrategia:**
- Configuración inicial: mapeo manual carpeta_id → buffet_id
- Future: auto-detección por nombre de carpeta o metadatos

### 7. CreateOficioFromDocumentPairUseCase

**Ubicación:** `src/modules/oficios/application/use_cases/create_oficio_from_document_pair.py`

**Responsabilidades:**
- Orquestar el proceso completo de creación de oficio desde par de documentos
- Combinar información de Oficio y CAV
- Enriquecer con Boostr API
- Crear oficio, vehículo, propietario, direcciones
- Guardar ambos PDFs como adjuntos

**Flujo:**
1. Recibir IDs de ambos documentos procesados
2. Descargar PDFs de Google Drive
3. Extraer texto de ambos PDFs
4. Identificar tipo de documento (Oficio vs CAV) si no está claro
5. Parsear con parser específico
6. Combinar información:
   - Número de oficio (del Oficio)
   - Vehículo (del CAV, preferencia alta)
   - Propietario (del Oficio, preferencia alta)
   - Direcciones (del Oficio, preferencia alta)
7. Consultar Boostr API:
   - GET /boostr/investigar/vehiculo/{patente}
   - GET /boostr/investigar/propietario/{rut}
8. Combinar datos (Boostr tiene preferencia sobre PDF)
9. Validar datos cruzados (RUT, patente deben coincidir)
10. Crear oficio usando CreateOficioUseCase
11. Guardar ambos PDFs como adjuntos:
    - Oficio: tipo DOCUMENTO, descripción "Oficio original"
    - CAV: tipo DOCUMENTO, descripción "CAV - Certificado de Inscripción"
12. Actualizar estados de documentos procesados a COMPLETADO

**DTOs necesarios:**
- `OficioExtraidoDTO`: Datos parseados del oficio
- `CAVExtraidoDTO`: Datos parseados del CAV
- `ParDocumentoDTO`: Contiene ambos DTOs + metadatos

### 8. Celery Task

**Ubicación:** `tasks/workers/process_drive_document_pair.py`

**Responsabilidades:**
- Procesar pares de documentos asíncronamente
- Manejar errores y retries
- Registrar actividad en timeline
- Notificar errores (opcional)

**Flujo:**
1. Recibir `drive_file_id` del documento nuevo
2. Buscar si existe par usando DocumentPairDetector
3. Si encuentra par:
   - Procesar ambos documentos juntos
   - Ejecutar CreateOficioFromDocumentPairUseCase
4. Si NO encuentra par:
   - Marcar estado como ESPERANDO_PAR
   - Opcional: Esperar timeout antes de procesar individual
5. Manejar errores y retries (máx 3 intentos)
6. Registrar en timeline si se crea oficio
7. Actualizar estados en DocumentoProcesadoModel

**Configuración Celery:**
- Broker: Redis (ya configurado)
- Retry: 3 intentos con backoff exponencial
- Timeout: 30 minutos por tarea

### 9. Webhook Endpoint

**Ubicación:** `src/modules/oficios/presentation/routers/drive_webhook_router.py`

**Responsabilidades:**
- Recibir notificaciones de Google Drive cuando se sube un archivo
- Validar webhook signature
- Crear registro en DocumentoProcesadoModel
- Detectar pares si es posible
- Encolar tarea Celery

**Endpoints:**
- `POST /oficios/drive/webhook`: Recibe notificación de Google Drive
- `POST /oficios/drive/process`: Procesamiento manual (para testing)

**Validaciones:**
- Webhook signature (Google Drive)
- Tipo de archivo (solo PDFs)
- Tamaño máximo (configurable)
- Deduplicación (`drive_file_id` único)

### 10. Modelo: DocumentoProcesado

**Ubicación:** `src/modules/oficios/infrastructure/models/documento_procesado_model.py`

**Campos:**
- `id`: Integer (PK)
- `drive_file_id`: String(255) (unique, index) - ID del archivo en Google Drive
- `drive_file_name`: String(500) - Nombre del archivo
- `drive_folder_id`: String(255) (index) - ID de la carpeta
- `tipo_documento`: Enum (oficio, cav, desconocido) (index)
- `par_documento_id`: Integer (FK a documentos_procesados.id, nullable, index)
- `buffet_id`: Integer (FK a buffets.id, nullable)
- `oficio_id`: Integer (FK a oficios.id, nullable, index)
- `estado`: Enum (pendiente, esperando_par, procesando, completado, error) (index)
- `datos_extraidos_json`: Text (JSON) - Datos parseados del documento
- `error_mensaje`: Text (nullable) - Mensaje de error si falla
- `created_at`: DateTime
- `updated_at`: DateTime

**Relaciones:**
- `par_documento_id` → `documentos_procesados.id` (self-referential, nullable)
- `buffet_id` → `buffets.id` (nullable)
- `oficio_id` → `oficios.id` (nullable)

**Propósito:**
- Tracking de archivos procesados
- Evitar duplicados
- Relacionar pares de documentos
- Detectar documentos faltantes
- Audit trail

### 11. Enums Adicionales

**Ubicación:** `src/shared/domain/enums.py`

**Nuevo enum: TipoDocumentoEnum**
```python
class TipoDocumentoEnum(str, Enum):
    """Tipos de documentos procesados desde Google Drive."""
    OFICIO = "oficio"  # Documento del oficio
    CAV = "cav"  # Certificado de Inscripción y Anotaciones Vigentes
    DESCONOCIDO = "desconocido"  # No se pudo identificar
```

**Nuevo enum: EstadoDocumentoProcesadoEnum**
```python
class EstadoDocumentoProcesadoEnum(str, Enum):
    """Estados de procesamiento de documentos."""
    PENDIENTE = "pendiente"  # Esperando procesamiento
    ESPERANDO_PAR = "esperando_par"  # Esperando el segundo documento del par
    PROCESANDO = "procesando"  # En proceso
    COMPLETADO = "completado"  # Procesado exitosamente
    ERROR = "error"  # Error en el procesamiento
```

**Actualizar TipoAdjuntoEnum:**
Agregar valores si es necesario (ya existe DOCUMENTO que es suficiente)

### 12. Configuración

**Archivo:** `src/core/config.py`

**Nuevas variables:**
- `GOOGLE_DRIVE_ENABLED: bool = False`
- `GOOGLE_DRIVE_FOLDER_ID: str = ""`
- `GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON: Optional[str] = None` (JSON como string o path)
- `GOOGLE_DRIVE_WEBHOOK_SECRET: Optional[str] = None`
- `PDF_OCR_ENABLED: bool = True`
- `PDF_OCR_LANGUAGE: str = "spa"`
- `DOCUMENT_PAIR_TIMEOUT_HOURS: int = 24` (horas para esperar segundo documento)

### 13. Dependencias Nuevas

**Archivo:** `requirements.txt`

Agregar:
- `PyPDF2==3.0.1` o `pdfplumber==0.10.3` (extracción de texto)
- `pytesseract==0.3.10` (OCR)
- `pdf2image==1.16.3` (convierte PDF a imágenes para OCR)
- `google-api-python-client==2.108.0` (Google Drive API)
- `google-auth==2.25.2` (Autenticación Google)
- `google-auth-httplib2==0.1.1`
- `google-auth-oauthlib==1.2.0`

**Nota:** `pdf2image` requiere `poppler` instalado en el sistema (paquete del sistema, no Python). En Docker, instalar en Dockerfile.

## Flujos Completos

### Flujo 1: Detección y Procesamiento Automático (Webhook)

```
1. Cliente sube PDF a Google Drive (carpeta específica del buffet)
   - Puede subir primero el Oficio o primero el CAV
   
2. Google Drive envía webhook a POST /oficios/drive/webhook

3. Endpoint valida:
   a. Webhook signature (Google Drive)
   b. Tipo de archivo (PDF)
   c. Tamaño máximo
   
4. Endpoint crea registro en DocumentoProcesadoModel:
   - drive_file_id, drive_file_name, drive_folder_id
   - estado: PENDIENTE
   - tipo_documento: DESCONOCIDO (se identifica después)
   
5. Endpoint intenta detectar par usando DocumentPairDetector:
   a. Busca en documentos_procesados por:
      - Misma carpeta (drive_folder_id)
      - Estado ESPERANDO_PAR
      - Fecha similar (dentro de DOCUMENT_PAIR_TIMEOUT_HOURS)
   b. Si encuentra match:
      - Actualiza ambos registros con par_documento_id
      - Cambia estados a PROCESANDO
      - Encola tarea Celery para procesar par completo
   c. Si NO encuentra match:
      - Marca estado como ESPERANDO_PAR
      - Encola tarea Celery (opcional: con delay para esperar segundo documento)
   
6. Celery Task (procesa par completo):
   a. Descarga ambos PDFs de Google Drive
   b. Extrae texto de ambos (PDFProcessor)
   c. Identifica tipo de documento (Oficio vs CAV) por contenido
   d. Parsea información con parser específico:
      - OficioParser: número oficio, propietario, direcciones, contexto legal
      - CAVParser: patente, marca, modelo, año, color, VIN
   e. Combina información de ambos documentos
   f. Mapea buffet por carpeta (BuffetMapper)
   g. Consulta Boostr API:
      - GET /boostr/investigar/vehiculo/{patente} (con oficio_id cuando exista)
      - GET /boostr/investigar/propietario/{rut} (con oficio_id cuando exista)
   h. Combina datos (Boostr tiene preferencia sobre PDF)
   i. Valida datos cruzados (RUT del Oficio debe coincidir con RUT de propietario en CAV/Boostr)
   j. Crea oficio usando CreateOficioUseCase
   k. Guarda ambos PDFs como adjuntos:
      - Oficio: tipo DOCUMENTO, descripción "Oficio original"
      - CAV: tipo DOCUMENTO, descripción "CAV - Certificado de Inscripción"
   l. Registra actividad en timeline
   m. Actualiza estado de ambos documentos a COMPLETADO
   
7. Si hay error:
   a. Registra error_mensaje en DocumentoProcesadoModel
   b. Cambia estado a ERROR
   c. Opcional: Notifica a administrador
```

### Flujo 2: Procesamiento Manual (Endpoint)

```
1. Cliente llama POST /oficios/drive/process
   
2. Request body:
   {
     "drive_file_id_oficio": "abc123",
     "drive_file_id_cav": "def456",
     "buffet_id": 1  // opcional, se infiere de carpeta
   }
   
3. Endpoint valida que ambos archivos existan en Google Drive
   
4. Endpoint crea/actualiza registros en DocumentoProcesadoModel
   
5. Endpoint encola tarea Celery para procesar par completo (mismo flujo que Flujo 1, paso 6)
   
6. Retorna task_id para tracking
```

### Flujo 3: Procesamiento de Documento Individual (cuando falta el par)

```
1. PDF detectado pero no se encuentra su par después de búsqueda
   
2. Estado marcado como ESPERANDO_PAR
   
3. Sistema espera DOCUMENT_PAIR_TIMEOUT_HOURS horas para que llegue el segundo documento
   
4. Si llega el segundo documento:
   - Se detecta el par automáticamente (Flujo 1, paso 5)
   - Se procesa el par completo
   
5. Si NO llega después del timeout:
   a. Procesa el documento individual con información parcial
   b. Crea oficio incompleto (requiere revisión manual)
   c. Marca estado como COMPLETADO con flag de "incompleto"
   d. Notifica al administrador
```

## Estructura de Archivos a Crear

```
src/
├── modules/oficios/
│   ├── application/
│   │   ├── use_cases/
│   │   │   └── create_oficio_from_document_pair.py
│   │   └── dtos/
│   │       ├── oficio_extraido_dto.py
│   │       ├── cav_extraido_dto.py
│   │       └── par_documento_dto.py
│   ├── infrastructure/
│   │   ├── models/
│   │   │   └── documento_procesado_model.py
│   │   ├── repositories/
│   │   │   └── documento_procesado_repository.py (opcional, para queries complejas)
│   │   └── services/
│   │       ├── oficio_parser.py
│   │       ├── cav_parser.py
│   │       ├── document_pair_detector.py
│   │       └── buffet_mapper.py
│   └── presentation/
│       └── routers/
│           └── drive_webhook_router.py
│
├── shared/
│   ├── domain/
│   │   └── enums.py (actualizar con nuevos enums)
│   └── infrastructure/
│       ├── external_apis/
│       │   └── google_drive/
│       │       ├── __init__.py
│       │       ├── client.py
│       │       ├── schemas.py
│       │       └── exceptions.py
│       └── services/
│           └── pdf_processor.py
│
└── tasks/
    └── workers/
        └── process_drive_document_pair.py
```

## Detalles de Implementación

### Detección de Tipo de Documento

**Estrategia:**
1. Analizar nombre de archivo (buscar keywords: "oficio", "cav", "certificado")
2. Analizar primeras líneas del texto extraído
3. Buscar patrones específicos:
   - Oficio: "OFICIO", "ROL", "Número de oficio", "Juzgado"
   - CAV: "CERTIFICADO DE INSCRIPCIÓN", "PATENTE", "MARCA", "MODELO"
4. Si no se identifica, marcar como DESCONOCIDO

### OficioParser - Estrategia de Parsing

**1. Número de Oficio:**
- Patrones: "OF-2024-001", "ROL-12345", "N° 123/2024"
- Regex: `(?:OF|OFICIO|ROL)[\s\-]*(?:N[°º]?\s*)?(\d+(?:\/\d+)?)`
- Buscar en primeras 20 líneas

**2. RUT del Propietario:**
- Formato chileno: "12.345.678-5" o "12345678-5"
- Regex: `(\d{1,2}\.?\d{3}\.?\d{3}[\-][\dkK])`
- Normalizar: quitar puntos, verificar dígito verificador

**3. Nombre Completo:**
- Buscar después de "PROPIETARIO:", "NOMBRE:", "SEÑOR/A:"
- Regex: `(?:PROPIETARIO|NOMBRE|SEÑOR[A]?)[\s:]+([A-ZÁÉÍÓÚÑ\s,\.]+)`
- Limpiar: mayúsculas, espacios múltiples

**4. Direcciones:**
- Buscar líneas con "DIRECCIÓN:", "DOMICILIO:", "DIR:"
- Regex: `(?:DIRECCIÓN|DOMICILIO|DIR)[\s:]+([A-Z0-9\s,#\.\-]+(?:COMUNA|REGION|CHILE)?)`
- Extraer comuna y región si están presentes
- Múltiples direcciones (una por línea o sección)

**5. Contexto Legal:**
- Buscar secciones como "MOTIVO:", "ASUNTO:", "ANTECEDENTES:"
- Extraer texto completo de la sección

### CAVParser - Estrategia de Parsing

**1. Patente:**
- Formato chileno: "ABCD12" o "AB1234"
- Regex: `[A-Z]{2,4}[\s\-]?\d{2,4}`
- Buscar después de "PATENTE:", "PLACA:"
- Normalizar: quitar espacios y guiones, convertir a mayúsculas

**2. Marca:**
- Buscar después de "MARCA:"
- Lista de marcas comunes (Toyota, Chevrolet, etc.)
- Normalizar variaciones (TOYOTA, Toyota, TOY)

**3. Modelo:**
- Buscar después de "MODELO:"
- Regex: `MODELO[\s:]+([A-Z0-9\s\-]+)`

**4. Año:**
- Buscar después de "AÑO:", "AÑO FABRICACIÓN:"
- Regex: `AÑO[\s:]+(\d{4})`

**5. Color:**
- Buscar después de "COLOR:"
- Lista de colores comunes
- Normalizar variaciones

**6. VIN:**
- Buscar después de "VIN:", "CHASIS:", "NÚMERO CHASIS:"
- Regex: `[A-HJ-NPR-Z0-9]{17}` (formato estándar VIN)

### DocumentPairDetector - Estrategias de Matching

**1. Por nombre de archivo:**
- Buscar nombres similares (mismo prefijo, misma fecha)
- Ejemplo: "OFICIO_2024_001.pdf" y "CAV_2024_001.pdf"

**2. Por fecha:**
- Archivos subidos en el mismo día o dentro de X horas
- Comparar `created_at` de metadatos de Google Drive

**3. Por contenido:**
- Si ya se procesó uno y se extrajo número de oficio o patente
- Buscar en `datos_extraidos_json` de otros documentos
- Matching por número de oficio o patente

**4. Por ubicación:**
- Misma carpeta de Google Drive (`drive_folder_id`)

**Algoritmo de matching:**
1. Buscar documentos en misma carpeta
2. Filtrar por estado ESPERANDO_PAR
3. Filtrar por fecha (dentro de DOCUMENT_PAIR_TIMEOUT_HOURS)
4. Si hay múltiples candidatos, priorizar:
   - Por fecha más cercana
   - Por tipo diferente (si uno es OFICIO, buscar CAV)
5. Si encuentra match, establecer `par_documento_id` bidireccional

### Combinación de Información (Oficio + CAV)

**Prioridad de Datos:**
1. **Número de Oficio**: Siempre del Oficio (única fuente)
2. **Vehículo**: 
   - Preferencia: Boostr > CAV > Oficio (si tiene)
   - Campos: patente, marca, modelo, año, color, VIN
3. **Propietario**:
   - Preferencia: Boostr > Oficio
   - Campos: RUT, nombre_completo, email, teléfono
4. **Direcciones**:
   - Preferencia: Oficio (múltiples) + Boostr (complementar)
   - Combinar listas, eliminar duplicados
5. **Contexto Legal**:
   - Solo del Oficio (únicamente está ahí)

**Validaciones Cruzadas:**
- RUT del propietario en Oficio debe coincidir con RUT en CAV/Boostr
- Patente en CAV debe coincidir con patente en Boostr
- Si hay discrepancias, registrar warning pero continuar (priorizar Boostr)

### Creación de Oficio

**Usar CreateOficioUseCase existente:**
- Pasar CreateOficioDTO con todos los datos combinados
- El use case maneja la creación de oficio, vehículo, propietarios, direcciones
- Retorna OficioResponseDTO

**Guardar Adjuntos:**
- Después de crear oficio, guardar ambos PDFs
- Usar servicio de storage existente
- Crear AdjuntoModel para cada PDF:
  - Oficio: tipo DOCUMENTO, descripción "Oficio original - Google Drive"
  - CAV: tipo DOCUMENTO, descripción "CAV - Certificado de Inscripción - Google Drive"

## Migración de Base de Datos

**Archivo:** `alembic/versions/xxxx_create_documento_procesado.py`

**Tabla:** `documentos_procesados`

**Campos:**
- `id`: Integer (PK, autoincrement)
- `drive_file_id`: String(255) (unique, index, not null)
- `drive_file_name`: String(500) (not null)
- `drive_folder_id`: String(255) (index, not null)
- `tipo_documento`: Enum (oficio, cav, desconocido) (index, not null, default='desconocido')
- `par_documento_id`: Integer (FK a documentos_procesados.id, nullable, index)
- `buffet_id`: Integer (FK a buffets.id, nullable)
- `oficio_id`: Integer (FK a oficios.id, nullable, index)
- `estado`: Enum (pendiente, esperando_par, procesando, completado, error) (index, not null, default='pendiente')
- `datos_extraidos_json`: Text (nullable, JSON)
- `error_mensaje`: Text (nullable)
- `created_at`: DateTime (timezone=True, not null, default=func.now())
- `updated_at`: DateTime (timezone=True, not null, default=func.now(), onupdate=func.now())

**Relaciones:**
- `par_documento_id` → `documentos_procesados.id` (self-referential, nullable, ondelete='SET NULL')
- `buffet_id` → `buffets.id` (nullable, ondelete='SET NULL')
- `oficio_id` → `oficios.id` (nullable, ondelete='SET NULL')

**Índices:**
- Unique: `drive_file_id`
- Index: `drive_folder_id`, `tipo_documento`, `par_documento_id`, `oficio_id`, `estado`
- Composite index: `(drive_folder_id, estado)` para búsquedas de pares

**Enums a crear:**
- `tipo_documento_enum`: oficio, cav, desconocido
- `estado_documento_procesado_enum`: pendiente, esperando_par, procesando, completado, error

## Seguridad y Validaciones

### 1. Webhook Validation
- Verificar signature de Google Drive (HMAC)
- Validar que el archivo es PDF (mime type)
- Validar tamaño máximo (configurable, default 10MB)
- Rate limiting en endpoint (evitar spam)

### 2. Deduplicación
- Verificar `drive_file_id` único en `documentos_procesados`
- No procesar el mismo archivo dos veces
- Si ya existe, retornar oficio_id existente (idempotencia)

### 3. Detección de Pares
- Buscar documentos pendientes en la misma carpeta
- Validar que no estén ya relacionados con otro par
- Timeout configurable para esperar segundo documento
- Límite de búsqueda (últimos 100 documentos en carpeta)

### 4. Mapeo Buffet
- Validar que la carpeta corresponde a un buffet activo
- Si no se encuentra, dejar `buffet_id` NULL y requerir asignación manual
- Log de advertencia cuando no se encuentra mapeo

### 5. Validación de Datos
- Validar formato de patente antes de consultar Boostr
- Validar RUT antes de consultar Boostr
- Validar número de oficio único antes de crear
- Validar coincidencia RUT entre Oficio y CAV/Boostr
- Si hay discrepancias, registrar pero continuar (priorizar Boostr)

## Testing

### Tests Unitarios

**1. OficioParser:**
- Test con texto de ejemplo de oficio real
- Test con variaciones de formato
- Test con datos faltantes
- Test de normalización (RUT, nombre, direcciones)

**2. CAVParser:**
- Test con texto de ejemplo de CAV real
- Test con variaciones de formato
- Test con datos faltantes
- Test de normalización (patente, marca, color)

**3. DocumentPairDetector:**
- Test de matching por nombre de archivo
- Test de matching por fecha
- Test de matching por contenido
- Test cuando no hay match
- Test cuando hay múltiples candidatos

**4. PDFProcessor:**
- Test con PDF de texto (PyPDF2)
- Test con PDF escaneado (OCR)
- Test con PDF corrupto
- Test con PDF protegido

**5. BuffetMapper:**
- Test de mapeo correcto
- Test cuando no existe mapeo
- Test con configuración vacía

### Tests de Integración

**1. CreateOficioFromDocumentPairUseCase:**
- Test con par completo (Oficio + CAV)
- Test con datos de Boostr
- Test con errores en Boostr (fallback a PDF)
- Test de validación cruzada (RUT, patente)
- Test de guardado de adjuntos

**2. Celery Task:**
- Test con par detectado
- Test con documento individual (esperando par)
- Test con timeout (documento individual)
- Test de retry en errores
- Test de registro en timeline

**3. Webhook Endpoint:**
- Test con webhook válido
- Test con webhook inválido (signature)
- Test con archivo no PDF
- Test de deduplicación
- Test de detección de par inmediata

**Mocks necesarios:**
- Google Drive API (httpx mock)
- Boostr API (httpx mock)
- PDFProcessor (mock de extracción de texto)
- Storage service (mock de guardado de archivos)

## Fases de Implementación

### Fase 1: Infraestructura Base (1-2 semanas)

**Objetivo:** Configurar servicios externos y procesamiento básico de PDFs

**Tareas:**
1. Configurar Google Drive API client con Service Account
2. Crear PDFProcessor (solo texto nativo, sin OCR)
3. Agregar configuración y variables de entorno
4. Crear enums (TipoDocumentoEnum, EstadoDocumentoProcesadoEnum)
5. Crear migración de base de datos
6. Tests básicos de Google Drive y PDFProcessor

**Entregables:**
- Google Drive client funcional
- PDFProcessor básico
- Modelo DocumentoProcesado en BD
- Configuración completa

### Fase 2: Parsing y Detección de Pares (2-3 semanas)

**Objetivo:** Extraer información de documentos y detectar pares

**Tareas:**
1. Crear OficioParser con regex patterns
2. Crear CAVParser con regex patterns
3. Crear DocumentPairDetector
4. Crear BuffetMapper (configuración básica)
5. Tests unitarios de parsers
6. Tests de detección de pares

**Entregables:**
- Parsers funcionales para Oficio y CAV
- Detección de pares funcionando
- Mapeo de carpetas a buffets

### Fase 3: Combinación y Enriquecimiento (2 semanas)

**Objetivo:** Combinar información y enriquecer con Boostr

**Tareas:**
1. Crear DTOs (OficioExtraidoDTO, CAVExtraidoDTO, ParDocumentoDTO)
2. Implementar lógica de combinación de información
3. Integrar con Boostr API
4. Crear CreateOficioFromDocumentPairUseCase
5. Tests de integración del use case

**Entregables:**
- Use case completo funcionando
- Integración con Boostr
- Guardado de adjuntos

### Fase 4: Automatización (1-2 semanas)

**Objetivo:** Procesamiento automático con webhooks y Celery

**Tareas:**
1. Crear Celery task para procesar pares
2. Crear webhook endpoint
3. Integrar con sistema de notificaciones (opcional)
4. Tests de integración completos
5. Registrar router en main.py

**Entregables:**
- Sistema completamente automatizado
- Webhook funcionando
- Celery tasks funcionando

### Fase 5: Mejoras y Robustez (1-2 semanas)

**Objetivo:** Mejorar calidad y manejo de edge cases

**Tareas:**
1. Agregar OCR como fallback (pdf2image + pytesseract)
2. Mejorar parsers (manejar más variaciones de formato)
3. Validación cruzada mejorada (Oficio vs CAV)
4. Manejo de errores mejorado
5. Logging estructurado
6. Tests de edge cases
7. Documentación

**Entregables:**
- Sistema robusto y completo
- OCR funcionando
- Tests completos
- Documentación actualizada

## Consideraciones Adicionales

### 1. Rate Limiting
- Google Drive API tiene límites (1000 requests/100s/user)
- Implementar rate limiting en cliente
- Cache de metadatos cuando sea posible

### 2. Performance
- Procesamiento asíncrono (Celery)
- Descarga de PDFs en paralelo cuando sea posible
- Cache de mapeo buffet → carpeta
- Índices en base de datos para búsquedas rápidas

### 3. Error Handling
- Si parsing falla, guardar PDF y permitir procesamiento manual
- Si Boostr falla, crear oficio con datos del PDF
- Si falta un documento del par, esperar timeout o procesar individual
- Registrar todos los errores en `documentos_procesados`
- Validar discrepancias entre Oficio y CAV (RUT, patente)

### 4. Monitoreo
- Logs estructurados para cada paso
- Métricas: archivos procesados, errores, tiempo de procesamiento
- Alertas para errores recurrentes
- Dashboard de documentos procesados (futuro)

### 5. Escalabilidad
- Celery workers escalables horizontalmente
- Base de datos con índices optimizados
- Storage de PDFs en S3 o similar (futuro)
- Cache de resultados de Boostr (futuro)

## Checklist de Implementación

### Infraestructura
- [ ] Google Drive API client configurado
- [ ] PDFProcessor implementado (texto + OCR)
- [ ] Configuración completa en config.py
- [ ] Enums creados en shared/domain/enums.py
- [ ] Migración de base de datos creada y aplicada

### Parsing
- [ ] OficioParser implementado
- [ ] CAVParser implementado
- [ ] Tests unitarios de parsers

### Detección y Combinación
- [ ] DocumentPairDetector implementado
- [ ] BuffetMapper implementado
- [ ] Lógica de combinación implementada
- [ ] Tests de detección de pares

### Use Case
- [ ] DTOs creados
- [ ] CreateOficioFromDocumentPairUseCase implementado
- [ ] Integración con Boostr
- [ ] Guardado de adjuntos
- [ ] Tests de integración

### Automatización
- [ ] Celery task implementado
- [ ] Webhook endpoint implementado
- [ ] Router registrado en main.py
- [ ] Tests de integración completos

### Mejoras
- [ ] OCR implementado
- [ ] Manejo de errores robusto
- [ ] Logging estructurado
- [ ] Documentación completa
