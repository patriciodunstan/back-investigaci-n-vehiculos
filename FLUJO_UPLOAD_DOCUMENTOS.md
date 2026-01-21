# Flujo de Upload y Procesamiento de Documentos

## 📋 Descripción General

Sistema de procesamiento batch de documentos para creación automática de oficios con investigación integrada.

**Flujo Completo:**
```
Frontend (Upload Batch)
    ↓
Backend (Procesa PDFs + Detecta Pares + Extrae Datos)
    ↓
Backend (Ejecuta Boostr API automáticamente)
    ↓
Backend (Crea Oficio Completo con Investigación)
    ↓
Frontend (Muestra Oficios Creados)
```

---

## 🚀 Endpoint Principal

### POST `/oficios/documents/upload-batch`

Sube múltiples documentos PDF (Oficio + CAV) para procesamiento automático.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `files` (file[], required): Archivos PDF (máx. 200 archivos)
- `buffet_id` (integer, optional): ID del buffet asociado

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8000/oficios/documents/upload-batch" \
  -H "Authorization: Bearer <token>" \
  -F "files=@oficio-001.pdf" \
  -F "files=@cav-001.pdf" \
  -F "buffet_id=1"
```

**Ejemplo con JavaScript (Frontend):**
```javascript
const formData = new FormData();
formData.append('files', oficioFile);
formData.append('files', cavFile);
formData.append('buffet_id', buffetId);

const response = await fetch('/oficios/documents/upload-batch', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
console.log(result);
```

**Response (202 Accepted):**
```json
{
  "task_ids": [
    "abc123_1705315200.123",
    "def456_1705315200.456"
  ],
  "total_files": 2,
  "processed_files": [
    {
      "file_id": "abc123",
      "file_name": "oficio-001.pdf",
      "storage_path": "/storage/2026/01/20/abc123_oficio-001.pdf",
      "tipo_documento": "oficio",
      "status": "processing"
    },
    {
      "file_id": "def456",
      "file_name": "cav-001.pdf",
      "storage_path": "/storage/2026/01/20/def456_cav-001.pdf",
      "tipo_documento": "cav",
      "status": "processing"
    }
  ],
  "buffet_id": 1,
  "status": "accepted",
  "message": "2 archivos subidos y en proceso"
}
```

---

## 🔄 Proceso Interno (Backend)

### 1. Validación y Almacenamiento
- Valida tipo de archivo (solo PDF)
- Valida tamaño (máx. 10MB por defecto)
- Guarda en storage local (`./storage/YYYY/MM/DD/`)
- Crea registro en tabla `documentos_procesados`

### 2. Detección de Tipo de Documento

El sistema detecta automáticamente el tipo basándose en:

**Keywords en nombre de archivo:**
- `oficio`, `of-` → Tipo: OFICIO
- `cav`, `certificado` → Tipo: CAV

**Keywords en contenido del PDF:**
- Oficio: "oficio", "rol", "juzgado"
- CAV: "certificado de inscripción", "patente", "marca", "modelo"

### 3. Extracción de Datos

**De Oficio:**
- Número de oficio
- Rol del tribunal
- Juzgado
- Fecha de emisión
- Patente del vehículo

**De CAV:**
- Patente
- Marca
- Modelo
- Año
- Color
- VIN/Chasis
- RUT propietario
- Nombre propietario

### 4. Emparejamiento de Documentos

El sistema detecta automáticamente pares de documentos:
- Busca Oficio + CAV con la **misma patente**
- Ventana de tiempo: 24 horas (configurable)
- Estado: `ESPERANDO_PAR` → `EMPAREJADO`

### 5. Investigación Automática con Boostr

**Si `ENABLE_BOOSTR_AUTO_INVESTIGATION=true` (por defecto):**

Al encontrar un par de documentos, ejecuta automáticamente:

1. **Consulta de Vehículo:**
   ```
   GET /boostr/vehiculo/{patente}
   ```
   Obtiene datos completos del vehículo

2. **Consulta de Multas:**
   ```
   GET /boostr/vehiculo/{patente}/multas
   ```
   Obtiene historial de multas

3. **Consulta de Propietario:**
   ```
   GET /boostr/persona/{rut}
   ```
   Obtiene datos del propietario

4. **Consulta de Otros Vehículos:**
   ```
   GET /boostr/persona/{rut}/vehiculos
   ```
   Obtiene otros vehículos a nombre del propietario

**Resultado:**
- Datos guardados en tabla `api_responses`
- Actividades registradas en timeline del oficio
- Investigación completa disponible inmediatamente

### 6. Creación Automática del Oficio

Con todos los datos recopilados, el sistema crea:

**Oficio:**
- Número de oficio
- Buffet asociado
- Estado: `pendiente`
- Prioridad: `media` (por defecto)

**Vehículo:**
- Patente, marca, modelo, año, color, VIN
- Datos combinados de CAV + Boostr

**Propietario:**
- RUT, nombre completo
- Tipo: `natural` o `juridica`
- Datos de CAV + Boostr

**Direcciones:**
- Dirección principal del CAV
- Tipo: `domicilio`

**Timeline:**
- Actividad de consulta Boostr
- Datos de investigación disponibles

---

## 📊 Estados del Proceso

Los documentos pasan por estos estados:

| Estado | Descripción |
|--------|-------------|
| `PENDIENTE` | Documento subido, esperando procesamiento |
| `ESPERANDO_PAR` | Documento procesado, esperando su par |
| `PROCESANDO` | Par completo encontrado, creando oficio |
| `COMPLETADO` | Oficio creado exitosamente |
| `ERROR` | Error durante el procesamiento |

**Consultar estado:**
```sql
SELECT
  file_id,
  file_name,
  tipo_documento,
  estado,
  oficio_id,
  error_mensaje
FROM documentos_procesados
WHERE buffet_id = 1
ORDER BY created_at DESC;
```

---

## ⚙️ Configuración

### Variables de Entorno

```env
# PDF Processing
PDF_OCR_ENABLED=false
PDF_OCR_LANGUAGE=spa
PDF_MAX_SIZE_MB=10
PDF_PROCESSING_TIMEOUT_SECONDS=300

# Document Pairing
DOCUMENT_PAIR_TIMEOUT_HOURS=24

# Boostr Integration
ENABLE_BOOSTR_AUTO_INVESTIGATION=true
BOOSTR_API_KEY=<tu_api_key>
```

### Habilitar OCR (Opcional)

Para PDFs escaneados (sin texto seleccionable):

1. **Instalar dependencias:**
   ```bash
   pip install pytesseract pdf2image pillow
   ```

2. **Instalar Tesseract OCR:**
   - **Windows:** Descargar de https://github.com/UB-Mannheim/tesseract/wiki
   - **Linux:** `sudo apt-get install tesseract-ocr tesseract-ocr-spa`
   - **macOS:** `brew install tesseract`

3. **Configurar en .env:**
   ```env
   PDF_OCR_ENABLED=true
   PDF_OCR_LANGUAGE=spa
   ```

---

## 🔍 Ejemplo Completo de Uso

### Paso 1: Preparar Documentos

Tener listo:
- `oficio-12345.pdf` - Documento del juzgado con orden de investigación
- `cav-ABCD12.pdf` - Certificado de Anotaciones Vigentes del vehículo

**Importante:** Ambos deben tener la **misma patente** para emparejarse automáticamente.

### Paso 2: Subir Documentos

```javascript
// Frontend - React/Vue/Angular
async function uploadDocuments(oficioFile, cavFile, buffetId) {
  const formData = new FormData();
  formData.append('files', oficioFile);
  formData.append('files', cavFile);
  formData.append('buffet_id', buffetId);

  const response = await fetch('/oficios/documents/upload-batch', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: formData
  });

  if (response.status === 202) {
    const result = await response.json();
    console.log('Documentos en proceso:', result.task_ids);

    // Opción 1: Polling para verificar estado
    setTimeout(() => checkStatus(result.task_ids), 5000);

    // Opción 2: Mostrar mensaje al usuario
    alert(`${result.total_files} documentos subidos. Procesando...`);
  }
}

async function checkStatus(taskIds) {
  // TODO: Implementar endpoint para consultar estado
  // GET /oficios/documents/status?task_ids=...
}
```

### Paso 3: El Backend Procesa Automáticamente

1. ✅ Guarda archivos en storage
2. ✅ Extrae texto de los PDFs
3. ✅ Detecta tipos (Oficio + CAV)
4. ✅ Empareja por patente
5. ✅ Ejecuta investigación Boostr
6. ✅ Crea oficio completo

**Tiempo estimado:** 10-30 segundos por par de documentos (depende de Boostr API)

### Paso 4: Consultar Oficios Creados

```bash
# Listar oficios del buffet
GET /oficios?buffet_id=1&limit=20

# Ver detalle de oficio con investigación
GET /oficios/{oficio_id}

# Ver timeline de investigación
GET /investigaciones/oficios/{oficio_id}/timeline
```

---

## 🎯 Mejores Prácticas

### Para el Frontend

1. **Upload en batch:** Subir múltiples pares a la vez (máx. 200 archivos)
2. **Mostrar progreso:** Indicar archivos subidos vs procesados
3. **Manejo de errores:** Validar archivos antes de subir (tipo, tamaño)
4. **Feedback al usuario:** Notificar cuando oficios estén listos

### Para Naming de Archivos

**Recomendado:**
- `oficio-12345.pdf` (incluye "oficio" en el nombre)
- `cav-ABCD12.pdf` (incluye "cav" o "certificado")

**También funciona:**
- `of-12345.pdf`
- `certificado-ABCD12.pdf`
- `patente-ABCD12-cav.pdf`

### Para Procesamiento Batch

**Opción 1: Upload Incremental**
```javascript
// Subir de a 10 documentos (5 pares)
for (let i = 0; i < files.length; i += 10) {
  const batch = files.slice(i, i + 10);
  await uploadBatch(batch);
  await sleep(1000); // Esperar 1 seg entre batches
}
```

**Opción 2: Upload Paralelo**
```javascript
// Subir todos de una vez (backend procesa async)
const formData = new FormData();
files.forEach(file => formData.append('files', file));
await fetch('/oficios/documents/upload-batch', {
  method: 'POST',
  body: formData
});
```

---

## 🐛 Troubleshooting

### Problema: Documentos no se emparejan

**Causas posibles:**
1. Patentes no coinciden exactamente
2. Documentos subidos con más de 24 horas de diferencia
3. Uno de los documentos no se pudo procesar

**Solución:**
```sql
-- Verificar documentos pendientes
SELECT file_name, tipo_documento, estado, datos_extraidos_json
FROM documentos_procesados
WHERE estado = 'ESPERANDO_PAR'
AND buffet_id = 1;

-- Revisar datos extraídos
SELECT
  file_name,
  tipo_documento,
  datos_extraidos_json->>'patente' as patente_extraida
FROM documentos_procesados
WHERE oficio_id IS NULL;
```

### Problema: Error al procesar PDF

**Causas posibles:**
1. PDF escaneado sin OCR habilitado
2. PDF corrupto o encriptado
3. Timeout de procesamiento

**Solución:**
- Habilitar OCR si es PDF escaneado
- Verificar que PDF no esté protegido con contraseña
- Aumentar `PDF_PROCESSING_TIMEOUT_SECONDS`

### Problema: Boostr API falla

**Causas posibles:**
1. API Key inválida
2. Rate limiting (máx. 60 req/min)
3. Patente no existe en base de datos Boostr

**Solución:**
- Verificar `BOOSTR_API_KEY` en .env
- Espaciar requests (backend ya lo hace automáticamente)
- Verificar patente en logs de error

---

## 📈 Monitoreo

### Métricas Importantes

```sql
-- Documentos procesados hoy
SELECT COUNT(*) as total, estado
FROM documentos_procesados
WHERE DATE(created_at) = CURRENT_DATE
GROUP BY estado;

-- Oficios creados desde documentos
SELECT COUNT(*) as total_oficios
FROM oficios
WHERE created_at >= CURRENT_DATE
AND id IN (
  SELECT oficio_id FROM documentos_procesados
  WHERE oficio_id IS NOT NULL
);

-- Tasa de éxito de emparejamiento
SELECT
  ROUND(100.0 * COUNT(CASE WHEN estado = 'COMPLETADO' THEN 1 END) / COUNT(*), 2) as tasa_exito_pct
FROM documentos_procesados
WHERE tipo_documento IN ('oficio', 'cav');
```

---

## 🔐 Seguridad

- ✅ Autenticación JWT requerida
- ✅ Validación de tipo de archivo (solo PDF)
- ✅ Validación de tamaño de archivo
- ✅ Storage local aislado por fecha
- ✅ Rate limiting en Boostr API
- ✅ Sanitización de nombres de archivo

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs de aplicación
2. Consultar tabla `documentos_procesados` para debugging
3. Verificar configuración de variables de entorno
4. Contactar al equipo de desarrollo
