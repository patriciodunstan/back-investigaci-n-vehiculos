# Implementación Final - Integración Google Drive

## ✅ Fases Completadas

### Fase 1: Infraestructura Base ✅
- ✅ Google Drive API Client (client, schemas, exceptions)
- ✅ PDFProcessor básico
- ✅ Configuración en `config.py`
- ✅ Enums (TipoDocumentoEnum, EstadoDocumentoProcesadoEnum)
- ✅ Modelo DocumentoProcesado y migración

### Fase 2: Parsers y Detección ✅
- ✅ OficioParser - Extrae datos de oficios
- ✅ CAVParser - Extrae datos de certificados CAV
- ✅ DocumentPairDetector - Detecta pares de documentos
- ✅ BuffetMapper - Mapea carpetas a buffets

### Fase 3: DTOs y UseCase ✅
- ✅ DTOs (OficioExtraidoDTO, CAVExtraidoDTO, ParDocumentoDTO)
- ✅ CreateOficioFromDocumentPairUseCase - Combina datos y crea oficios

### Fase 4: Celery Task y Webhook ✅
- ✅ Celery task (`process_drive_document_pair`) - Procesa documentos asíncronamente
- ✅ Webhook endpoint (`/oficios/drive/webhook`) - Recibe notificaciones de Google Drive
- ✅ Endpoint manual (`/oficios/drive/process`) - Para testing

### Fase 5: OCR como Fallback ✅
- ✅ OCR integrado en PDFProcessor usando pytesseract + pdf2image
- ✅ Fallback automático cuando PyPDF2/pdfplumber fallan

---

## 📦 Dependencias Requeridas

### Básicas (Ya instaladas)
- `fastapi`, `sqlalchemy`, `pydantic`, etc.

### Google Drive API
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### PDF Processing
```bash
pip install PyPDF2 pdfplumber
```

### OCR (Opcional, para Fase 5)
```bash
pip install pytesseract pdf2image pillow
```

**Nota:** Para OCR también necesitas instalar Tesseract OCR:
- **Windows:** Descargar de https://github.com/UB-Mannheim/tesseract/wiki
- **Linux:** `sudo apt-get install tesseract-ocr`
- **macOS:** `brew install tesseract`

---

## 🔧 Configuración

### 1. Variables de Entorno

Agregar al archivo `.env`:

```env
# Google Drive Integration
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id_aqui
GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
# O como path: GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON=./config/service-account.json
GOOGLE_DRIVE_WEBHOOK_SECRET=tu_secreto_aleatorio
GOOGLE_DRIVE_BUFFET_MAPPING={"folder_id_1":1,"folder_id_2":2}

# PDF Processing
PDF_OCR_ENABLED=true
PDF_OCR_LANGUAGE=spa
PDF_MAX_SIZE_MB=10
PDF_PROCESSING_TIMEOUT_SECONDS=300

# Document Pairing
DOCUMENT_PAIR_TIMEOUT_HOURS=24
```

### 2. Obtener Credenciales

Ver `GUIA_CREDENCIALES_GOOGLE.md` para instrucciones detalladas.

**Resumen rápido:**
1. Crear proyecto en Google Cloud Console
2. Habilitar Google Drive API
3. Crear Service Account
4. Descargar key JSON
5. Compartir carpeta de Google Drive con el email de la Service Account
6. Configurar variables de entorno

---

## 🗄️ Migración de Base de Datos

Aplicar la migración:

```bash
alembic upgrade head
```

Esto creará la tabla `documentos_procesados` con todos los campos necesarios.

---

## 🚀 Uso

### Endpoint de Webhook

Google Drive puede enviar notificaciones a:
```
POST /oficios/drive/webhook
```

### Endpoint Manual (Testing)

Para procesar un documento manualmente:
```
POST /oficios/drive/process
Body: {
  "drive_file_id": "abc123..."
}
```

---

## 📝 Notas Importantes

### Pendientes (Opcionales)

1. **Guardar PDFs como adjuntos**
   - Actualmente los PDFs se descargan pero no se guardan como adjuntos
   - Se puede implementar después usando el sistema de storage existente

2. **Validación de Webhook Signature**
   - Actualmente el webhook acepta cualquier request
   - En producción, agregar validación HMAC de Google Drive

3. **Tests**
   - Agregar tests unitarios e integración
   - Mockear Google Drive API para tests

4. **Celery Configuration**
   - La task está lista pero requiere configuración de Celery
   - Ver `tasks/workers/process_drive_document_pair.py` para más detalles

---

## 📚 Archivos Creados

### Fase 1
- `src/shared/infrastructure/external_apis/google_drive/` (4 archivos)
- `src/shared/infrastructure/services/pdf_processor.py`
- `src/modules/oficios/infrastructure/models/documento_procesado_model.py`
- Migración Alembic

### Fase 2
- `src/modules/oficios/infrastructure/services/oficio_parser.py`
- `src/modules/oficios/infrastructure/services/cav_parser.py`
- `src/modules/oficios/infrastructure/services/document_pair_detector.py`
- `src/modules/oficios/infrastructure/services/buffet_mapper.py`

### Fase 3
- `src/modules/oficios/application/dtos/documento_extraido_dto.py`
- `src/modules/oficios/application/use_cases/create_oficio_from_document_pair.py`

### Fase 4
- `tasks/workers/process_drive_document_pair.py`
- `src/modules/oficios/presentation/routers/drive_webhook_router.py`
- `src/modules/oficios/presentation/schemas/drive_webhook_schemas.py`

### Fase 5
- OCR agregado a `pdf_processor.py`

### Documentación
- `GUIA_CREDENCIALES_GOOGLE.md`
- `IMPLEMENTACION_COMPLETA_FASES_1_4.md`
- `IMPLEMENTACION_FINAL.md` (este archivo)

---

## ✅ Checklist de Implementación

- [x] Google Drive API Client
- [x] PDFProcessor con OCR
- [x] Parsers (Oficio, CAV)
- [x] Detección de pares
- [x] Mapeo de carpetas a buffets
- [x] DTOs y UseCase
- [x] Celery task
- [x] Webhook endpoint
- [x] Router registrado en main.py
- [x] Migración creada
- [ ] Credenciales de Google configuradas
- [ ] Migración aplicada
- [ ] Dependencias instaladas
- [ ] Tests (opcional)

---

## 🎯 Próximos Pasos

1. **Obtener credenciales de Google** (ver `GUIA_CREDENCIALES_GOOGLE.md`)
2. **Instalar dependencias**
3. **Aplicar migración**
4. **Configurar variables de entorno**
5. **Probar endpoints**
6. **Configurar webhook en Google Drive** (opcional)
