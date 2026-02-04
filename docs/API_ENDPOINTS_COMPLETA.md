# Documentación Completa de API Endpoints

## Sistema de Investigaciones Vehiculares - Backend FastAPI

**Versión:** 1.0.0  
**Base URL:** `/`  
**Documentación Swagger:** `/docs`  
**Documentación ReDoc:** `/redoc`

---

## Índice

1. [Resumen General](#resumen-general)
2. [Autenticación](#autenticación)
3. [Módulo Sistema](#módulo-sistema)
4. [Módulo Usuarios](#módulo-usuarios)
5. [Módulo Buffets](#módulo-buffets)
6. [Módulo Oficios](#módulo-oficios)
7. [Módulo Investigaciones](#módulo-investigaciones)
8. [Módulo Boostr API](#módulo-boostr-api)
9. [Módulo Notificaciones](#módulo-notificaciones)
10. [Endpoints No Registrados](#endpoints-no-registrados)
11. [Códigos de Error](#códigos-de-error)
12. [Observaciones y Pendientes](#observaciones-y-pendientes)

---

## Resumen General

| Categoría | Cantidad |
|-----------|----------|
| **Total de Endpoints** | 31 |
| **Endpoints Públicos** | 6 |
| **Endpoints Protegidos (JWT)** | 25 |
| **Endpoints Solo Admin** | 4 |
| **Endpoints Admin/Investigador** | 1 |

### Registro de Routers en `main.py`

```python
app.include_router(auth_router)              # /auth
app.include_router(usuarios_router)          # /usuarios
app.include_router(buffet_router)            # /buffets
app.include_router(oficio_router)            # /oficios
app.include_router(document_upload_router)   # /oficios/documents
app.include_router(investigacion_router)     # /investigaciones
app.include_router(boostr_router)            # /boostr
app.include_router(notificacion_router)      # /notificaciones
```

---

## Autenticación

El sistema utiliza **OAuth2 con JWT Bearer Tokens**.

### Obtención del Token

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=email@ejemplo.com&password=mipassword
```

### Uso del Token

```http
Authorization: Bearer <access_token>
```

### Roles del Sistema

| Rol | Descripción |
|-----|-------------|
| `admin` | Acceso completo, gestión de usuarios y buffets |
| `investigador` | Creación y gestión de oficios, investigaciones |
| `cliente` | Vista limitada a oficios de su buffet |

---

## Módulo Sistema

**Prefijo:** `/`  
**Tags:** `Sistema`

Endpoints para monitoreo y estado de la aplicación.

### Endpoints

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/` | Endpoint raíz de la API | ❌ |
| `GET` | `/health` | Health check del sistema | ❌ |
| `GET` | `/info` | Información del sistema | ❌ |

---

### `GET /` - Raíz

**Descripción:** Endpoint raíz de la API.

**Respuesta:**
```json
{
  "app": "Sistema Investigaciones Vehiculares",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

---

### `GET /health` - Health Check

**Descripción:** Verifica el estado de la API.

**Respuesta:**
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "connected"
}
```

---

### `GET /info` - Información del Sistema

**Descripción:** Retorna información general del sistema.

**Respuesta:**
```json
{
  "app_name": "Sistema Investigaciones Vehiculares",
  "version": "1.0.0",
  "environment": "production",
  "debug": false,
  "api_version": "v1"
}
```

---

## Módulo Usuarios

### Autenticación (`/auth`)

**Prefijo:** `/auth`  
**Tags:** `Autenticacion`

Endpoints para registro, login y gestión de sesión.

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/auth/register` | Registrar nuevo usuario | ❌ |
| `POST` | `/auth/login` | Login (form-data OAuth2) | ❌ |
| `POST` | `/auth/login/json` | Login (JSON body) | ❌ |
| `GET` | `/auth/me` | Obtener usuario actual | ✅ JWT |

---

### `POST /auth/register` - Registrar Usuario

**Descripción:** Crea un nuevo usuario en el sistema.

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password123",
  "nombre": "Juan Pérez",
  "rol": "investigador",
  "buffet_id": 1
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `email` | string | ✅ | Email único del usuario |
| `password` | string | ✅ | Contraseña (mínimo 6 caracteres) |
| `nombre` | string | ✅ | Nombre completo |
| `rol` | string | ✅ | `admin`, `investigador`, `cliente` |
| `buffet_id` | int | ⚠️ | Requerido para rol `cliente` |

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "nombre": "Juan Pérez",
  "rol": "investigador",
  "buffet_id": null,
  "activo": true,
  "avatar_url": null,
  "created_at": "2026-02-04T10:00:00Z",
  "updated_at": "2026-02-04T10:00:00Z"
}
```

**Errores:**
- `409 Conflict`: Email ya registrado
- `400 Bad Request`: Datos inválidos

---

### `POST /auth/login` - Login (OAuth2 Form)

**Descripción:** Autentica un usuario y retorna token JWT.

**Request:** `application/x-www-form-urlencoded`
```
username=usuario@ejemplo.com&password=password123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errores:**
- `401 Unauthorized`: Email o contraseña incorrectos
- `403 Forbidden`: Usuario inactivo

---

### `POST /auth/login/json` - Login (JSON)

**Descripción:** Login alternativo usando JSON body.

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password123"
}
```

**Response:** Igual que `/auth/login`

---

### `GET /auth/me` - Usuario Actual

**Descripción:** Obtiene los datos del usuario autenticado.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "nombre": "Juan Pérez",
  "rol": "investigador",
  "buffet_id": null,
  "activo": true,
  "avatar_url": null,
  "created_at": "2026-02-04T10:00:00Z",
  "updated_at": "2026-02-04T10:00:00Z"
}
```

---

### Gestión de Usuarios (`/usuarios`)

**Prefijo:** `/usuarios`  
**Tags:** `Usuarios`

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/usuarios` | Listar usuarios (paginado) | ✅ JWT |

---

### `GET /usuarios` - Listar Usuarios

**Descripción:** Lista usuarios del sistema con paginación y filtros.

**Query Parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros a saltar |
| `limit` | int | 100 | Máximo de registros (max 100) |
| `activo_only` | bool | true | Solo usuarios activos |
| `rol` | string | null | Filtrar por rol |
| `buffet_id` | int | null | Filtrar por buffet |

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "email": "admin@ejemplo.com",
      "nombre": "Admin Sistema",
      "rol": "admin",
      "buffet_id": null,
      "activo": true,
      "avatar_url": null,
      "created_at": "2026-02-04T10:00:00Z",
      "updated_at": "2026-02-04T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

---

## Módulo Buffets

**Prefijo:** `/buffets`  
**Tags:** `Buffets`

Gestión de estudios jurídicos (clientes).

| Método | Path | Descripción | Auth | Permisos |
|--------|------|-------------|------|----------|
| `GET` | `/buffets` | Listar buffets | ✅ JWT | Todos |
| `GET` | `/buffets/{id}` | Obtener buffet por ID | ✅ JWT | Todos |
| `POST` | `/buffets` | Crear buffet | ✅ JWT | **Solo Admin** |
| `PUT` | `/buffets/{id}` | Actualizar buffet | ✅ JWT | Todos |
| `DELETE` | `/buffets/{id}` | Eliminar buffet (soft) | ✅ JWT | **Solo Admin** |

---

### `GET /buffets` - Listar Buffets

**Query Parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros a saltar |
| `limit` | int | 100 | Máximo de registros |
| `activo_only` | bool | true | Solo buffets activos |

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Buffet García & Asociados",
      "rut": "76.123.456-7",
      "email_principal": "contacto@buffetgarcia.cl",
      "telefono": "+56912345678",
      "contacto_nombre": "María García",
      "token_tablero": "abc123token",
      "activo": true,
      "created_at": "2026-02-04T10:00:00Z",
      "updated_at": "2026-02-04T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

---

### `GET /buffets/{buffet_id}` - Obtener Buffet

**Path Parameters:**
- `buffet_id` (int): ID del buffet

**Response:** `200 OK` - Objeto BuffetResponse

**Errores:**
- `404 Not Found`: Buffet no existe

---

### `POST /buffets` - Crear Buffet

**⚠️ Solo Admin**

**Request Body:**
```json
{
  "nombre": "Buffet García & Asociados",
  "rut": "76.123.456-7",
  "email_principal": "contacto@buffetgarcia.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "María García"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nombre` | string | ✅ | Nombre del buffet |
| `rut` | string | ✅ | RUT único de la empresa |
| `email_principal` | string | ✅ | Email de contacto |
| `telefono` | string | ❌ | Teléfono de contacto |
| `contacto_nombre` | string | ❌ | Nombre del contacto |

**Response:** `201 Created`

**Errores:**
- `403 Forbidden`: No es admin
- `409 Conflict`: RUT ya existe
- `400 Bad Request`: Datos inválidos

---

### `PUT /buffets/{buffet_id}` - Actualizar Buffet

**Request Body:**
```json
{
  "nombre": "Nuevo Nombre",
  "email_principal": "nuevo@email.cl",
  "telefono": "+56998765432",
  "contacto_nombre": "Pedro López"
}
```

**Response:** `200 OK`

---

### `DELETE /buffets/{buffet_id}` - Eliminar Buffet

**⚠️ Solo Admin**

**Descripción:** Desactiva un buffet (soft delete).

**Response:** `204 No Content`

**Errores:**
- `403 Forbidden`: No es admin
- `404 Not Found`: Buffet no existe

---

## Módulo Oficios

**Prefijo:** `/oficios`  
**Tags:** `Oficios`

Gestión de oficios de investigación vehicular.

### Endpoints Principales

| Método | Path | Descripción | Auth | Permisos |
|--------|------|-------------|------|----------|
| `GET` | `/oficios` | Listar oficios | ✅ JWT | Todos |
| `GET` | `/oficios/{id}` | Obtener oficio | ✅ JWT | Todos |
| `POST` | `/oficios` | Crear oficio | ✅ JWT | **Admin/Investigador** |
| `PUT` | `/oficios/{id}` | Actualizar oficio | ✅ JWT | Todos |
| `PATCH` | `/oficios/{id}/asignar` | Asignar investigador | ✅ JWT | **Solo Admin** |
| `PATCH` | `/oficios/{id}/estado` | Cambiar estado | ✅ JWT | Todos |

### Endpoints de Propietarios y Direcciones

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/oficios/{id}/propietarios` | Agregar propietario | ✅ JWT |
| `POST` | `/oficios/{id}/direcciones` | Agregar dirección | ✅ JWT |

### Endpoints de Visitas

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/oficios/direcciones/{id}/visitas` | Registrar visita | ✅ JWT |
| `GET` | `/oficios/direcciones/{id}/visitas` | Historial de visitas | ✅ JWT |
| `GET` | `/oficios/{id}/direcciones/pendientes` | Direcciones pendientes | ✅ JWT |

---

### `GET /oficios` - Listar Oficios

**Query Parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros a saltar |
| `limit` | int | 20 | Máximo (1-100) |
| `buffet_id` | int | null | Filtrar por buffet |
| `investigador_id` | int | null | Filtrar por investigador |
| `estado` | string | null | Filtrar por estado |

**Estados disponibles:** `pendiente`, `en_investigacion`, `cerrado`, `archivado`

**Nota:** Si el usuario es `cliente`, solo ve oficios de su buffet.

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "numero_oficio": "OF-2026-001",
      "buffet_id": 1,
      "buffet_nombre": "Buffet García",
      "investigador_id": 2,
      "investigador_nombre": "Juan Investigador",
      "estado": "en_investigacion",
      "prioridad": "alta",
      "fecha_ingreso": "2026-02-04T10:00:00Z",
      "fecha_limite": "2026-02-28T23:59:59Z",
      "notas_generales": "Urgente",
      "created_at": "2026-02-04T10:00:00Z",
      "updated_at": "2026-02-04T10:00:00Z",
      "vehiculos": [...],
      "propietarios": [...],
      "direcciones": [...]
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

---

### `POST /oficios` - Crear Oficio

**⚠️ Solo Admin o Investigador**

**Request Body:**
```json
{
  "numero_oficio": "OF-2026-001",
  "buffet_id": 1,
  "vehiculo": {
    "patente": "ABCD12",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "color": "Blanco",
    "vin": "1HGBH41JXMN109186"
  },
  "prioridad": "alta",
  "fecha_limite": "2026-02-28T23:59:59Z",
  "notas_generales": "Investigación urgente",
  "propietarios": [
    {
      "rut": "12.345.678-9",
      "nombre_completo": "Pedro González",
      "tipo": "titular",
      "email": "pedro@email.com",
      "telefono": "+56912345678",
      "direccion_principal": "Av. Principal 123",
      "notas": "Contactar por email"
    }
  ],
  "direcciones": [
    {
      "direccion": "Av. Principal 123, Depto 45",
      "comuna": "Santiago",
      "region": "Metropolitana",
      "tipo": "domicilio",
      "notas": "Edificio con conserje"
    }
  ]
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `numero_oficio` | string | ✅ | Número único del oficio |
| `buffet_id` | int | ✅ | ID del buffet asociado |
| `vehiculo` | object | ✅ | Datos del vehículo |
| `prioridad` | string | ❌ | `baja`, `media`, `alta`, `urgente` |
| `fecha_limite` | datetime | ❌ | Fecha límite de investigación |
| `notas_generales` | string | ❌ | Notas adicionales |
| `propietarios` | array | ❌ | Lista de propietarios |
| `direcciones` | array | ❌ | Lista de direcciones |

**Response:** `201 Created`

**Errores:**
- `403 Forbidden`: No tiene permisos
- `409 Conflict`: Número de oficio ya existe
- `400 Bad Request`: Datos inválidos

---

### `PATCH /oficios/{oficio_id}/asignar` - Asignar Investigador

**⚠️ Solo Admin**

**Request Body:**
```json
{
  "investigador_id": 2
}
```

**Response:** `200 OK` - Oficio actualizado

---

### `PATCH /oficios/{oficio_id}/estado` - Cambiar Estado

**Request Body:**
```json
{
  "estado": "cerrado"
}
```

**Estados válidos:** `pendiente`, `en_investigacion`, `cerrado`, `archivado`

---

### `POST /oficios/{oficio_id}/propietarios` - Agregar Propietario

**Request Body:**
```json
{
  "rut": "12.345.678-9",
  "nombre_completo": "María López",
  "tipo": "titular",
  "email": "maria@email.com",
  "telefono": "+56912345678",
  "direccion_principal": "Calle Nueva 456",
  "notas": "Propietaria anterior"
}
```

**Tipos de propietario:** `titular`, `cotitular`, `representante`, `anterior`

---

### `POST /oficios/{oficio_id}/direcciones` - Agregar Dirección

**Request Body:**
```json
{
  "direccion": "Calle Nueva 456",
  "comuna": "Providencia",
  "region": "Metropolitana",
  "tipo": "domicilio",
  "notas": "Casa particular"
}
```

**Tipos de dirección:** `domicilio`, `trabajo`, `referencia`, `otro`

---

### `POST /oficios/direcciones/{direccion_id}/visitas` - Registrar Visita

**Descripción:** Registra una visita a una dirección y actualiza su estado de verificación.

**Request Body:**
```json
{
  "resultado": "exitosa",
  "notas": "Se contactó al propietario, confirmó domicilio",
  "latitud": -33.4489,
  "longitud": -70.6693
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `resultado` | string | ✅ | Resultado de la visita |
| `notas` | string | ❌ | Observaciones |
| `latitud` | float | ❌ | Coordenada GPS |
| `longitud` | float | ❌ | Coordenada GPS |

**Resultados posibles:**
- `exitosa`: Se encontró al propietario/vehículo
- `no_encontrado`: Nadie en el domicilio
- `direccion_incorrecta`: La dirección no existe o es errónea
- `se_mudo`: El propietario ya no vive ahí
- `rechazo_atencion`: Se negaron a atender
- `otro`: Otro resultado

**Response:** `201 Created`
```json
{
  "id": 1,
  "direccion_id": 5,
  "investigador_id": 2,
  "investigador_nombre": "Juan Pérez",
  "fecha_visita": "2026-02-04T15:30:00Z",
  "resultado": "exitosa",
  "notas": "Se contactó al propietario",
  "latitud": -33.4489,
  "longitud": -70.6693
}
```

---

### `GET /oficios/direcciones/{direccion_id}/visitas` - Historial de Visitas

**Response:** `200 OK` - Lista de visitas ordenadas por fecha (más reciente primero)

---

### `GET /oficios/{oficio_id}/direcciones/pendientes` - Direcciones Pendientes

**Descripción:** Obtiene las direcciones de un oficio que requieren verificación.

**Incluye:**
- Direcciones nunca visitadas (pendiente)
- Direcciones con resultado `no_encontrado` (intentar de nuevo)
- Direcciones con rechazo de atención (intentar de nuevo)

---

## Módulo Documentos

**Prefijo:** `/oficios/documents`  
**Tags:** `Documentos`

Subida y procesamiento de documentos PDF.

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/oficios/documents/upload-batch` | Subida masiva de PDFs | ✅ JWT |

---

### `POST /oficios/documents/upload-batch` - Subida Masiva

**Descripción:** Sube múltiples documentos PDF (Oficio + CAV) para procesamiento automático.

**Request:** `multipart/form-data`

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `files` | file[] | ✅ | Archivos PDF (hasta 200) |
| `buffet_id` | int | ❌ | ID del buffet asociado |

**Response:** `202 Accepted`
```json
{
  "task_ids": ["abc123_1707048000.0"],
  "total_files": 2,
  "processed_files": [
    {
      "file_id": "abc123",
      "file_name": "OF-001.pdf",
      "storage_path": "/storage/abc123.pdf",
      "tipo_documento": "oficio",
      "status": "processing"
    },
    {
      "file_id": "def456",
      "file_name": "CAV-001.pdf",
      "storage_path": "/storage/def456.pdf",
      "tipo_documento": "cav",
      "status": "processing"
    }
  ],
  "buffet_id": 1,
  "status": "accepted",
  "message": "2 archivos subidos y en proceso"
}
```

**Errores:**
- `400 Bad Request`: Más de 200 archivos o ningún archivo
- `400 Bad Request`: Tipo de archivo no permitido
- `500 Internal Server Error`: Error en procesamiento

---

## Módulo Investigaciones

**Prefijo:** `/investigaciones`  
**Tags:** `Investigaciones`

Timeline de actividades y avistamientos.

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/investigaciones/oficios/{id}/timeline` | Obtener timeline | ✅ JWT |
| `POST` | `/investigaciones/oficios/{id}/actividades` | Agregar actividad | ✅ JWT |
| `POST` | `/investigaciones/oficios/{id}/avistamientos` | Registrar avistamiento | ✅ JWT |

---

### `GET /investigaciones/oficios/{oficio_id}/timeline` - Timeline

**Query Parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `limit` | int | 50 | Máximo de items (1-200) |

**Response:** `200 OK`
```json
{
  "oficio_id": 1,
  "items": [
    {
      "tipo": "actividad",
      "id": 1,
      "fecha": "2026-02-04T15:30:00Z",
      "descripcion": "Consulta a Boostr API",
      "detalle": "Se consultó información del RUT 12.345.678-9",
      "fuente": "boostr_api",
      "investigador_id": 2
    },
    {
      "tipo": "avistamiento",
      "id": 2,
      "fecha": "2026-02-04T16:00:00Z",
      "descripcion": "Avistamiento en Providencia",
      "detalle": "Vehículo estacionado en Av. Providencia 1500",
      "fuente": "terreno",
      "investigador_id": null
    }
  ],
  "total": 2
}
```

---

### `POST /investigaciones/oficios/{oficio_id}/actividades` - Agregar Actividad

**Request Body:**
```json
{
  "tipo_actividad": "consulta_api",
  "descripcion": "Consulta de vehículos por RUT",
  "resultado": "Se encontraron 3 vehículos",
  "api_externa": "boostr",
  "datos_json": {"vehiculos_encontrados": 3}
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `tipo_actividad` | string | ✅ | Tipo de actividad |
| `descripcion` | string | ✅ | Descripción de la actividad |
| `resultado` | string | ❌ | Resultado obtenido |
| `api_externa` | string | ❌ | API externa consultada |
| `datos_json` | object | ❌ | Datos adicionales en JSON |

**Tipos de actividad:** `consulta_api`, `visita_terreno`, `llamada_telefonica`, `revision_documentos`, `otro`

---

### `POST /investigaciones/oficios/{oficio_id}/avistamientos` - Registrar Avistamiento

**Request Body:**
```json
{
  "fuente": "terreno",
  "ubicacion": "Av. Providencia 1500, Providencia",
  "fecha_hora": "2026-02-04T16:00:00Z",
  "latitud": -33.4289,
  "longitud": -70.6188,
  "notas": "Vehículo estacionado, sin ocupantes"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `fuente` | string | ✅ | Origen del avistamiento |
| `ubicacion` | string | ✅ | Ubicación del avistamiento |
| `fecha_hora` | datetime | ✅ | Fecha y hora del avistamiento |
| `latitud` | float | ❌ | Coordenada GPS |
| `longitud` | float | ❌ | Coordenada GPS |
| `notas` | string | ❌ | Observaciones |

**Fuentes:** `terreno`, `camaras`, `denuncia_ciudadana`, `api_externa`, `otro`

---

## Módulo Boostr API

**Prefijo:** `/boostr`  
**Tags:** `Boostr API`

Integración con API externa Boostr (Rutificador) para consultas por RUT.

| Método | Path | Descripción | Auth | Créditos |
|--------|------|-------------|------|----------|
| `GET` | `/boostr/rut/vehicles/{rut}` | Consultar vehículos | ✅ JWT | 1 |
| `GET` | `/boostr/rut/properties/{rut}` | Consultar propiedades | ✅ JWT | 1 |
| `GET` | `/boostr/rut/deceased/{rut}` | Verificar defunción | ✅ JWT | 1 |
| `GET` | `/boostr/investigar/propietario/{rut}` | Investigación completa | ✅ JWT | 3 |

---

### `GET /boostr/rut/vehicles/{rut}` - Vehículos por RUT

**Path Parameters:**
- `rut` (string): RUT de la persona o empresa (ej: 12.345.678-9)

**Response:** `200 OK`
```json
[
  {
    "patente": "ABCD12",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "tipo": "automovil"
  }
]
```

**Errores:**
- `400 Bad Request`: RUT inválido
- `429 Too Many Requests`: Rate limit excedido
- `401 Unauthorized`: Error de autenticación con Boostr
- `502 Bad Gateway`: Error en servicio externo

---

### `GET /boostr/rut/properties/{rut}` - Propiedades por RUT

**Response:** `200 OK`
```json
[
  {
    "rol": "1234-5678",
    "comuna": "Santiago",
    "direccion": "Av. Principal 123",
    "destino": "habitacional",
    "avaluo": 150000000
  }
]
```

---

### `GET /boostr/rut/deceased/{rut}` - Verificar Defunción

**Response:** `200 OK`
```json
{
  "rut": "12.345.678-9",
  "fallecido": false,
  "fecha_defuncion": null
}
```

---

### `GET /boostr/investigar/propietario/{rut}` - Investigación Completa

**Descripción:** Obtiene toda la información de un propietario en una sola llamada.

**Response:** `200 OK`
```json
{
  "rut": "12.345.678-9",
  "vehiculos": [...],
  "propiedades": [...],
  "fallecido": false,
  "fecha_defuncion": null
}
```

**⚠️ Consume 3 créditos de Boostr**

---

## Módulo Notificaciones

**Prefijo:** `/notificaciones`  
**Tags:** `Notificaciones`

Sistema de notificaciones por email.

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/notificaciones/oficios/{id}/notificaciones` | Historial de notificaciones | ✅ JWT |
| `POST` | `/notificaciones/oficios/{id}/notificaciones` | Enviar notificación | ✅ JWT |

---

### `GET /notificaciones/oficios/{oficio_id}/notificaciones` - Historial

**Response:** `200 OK`
```json
{
  "oficio_id": 1,
  "items": [
    {
      "id": 1,
      "oficio_id": 1,
      "tipo": "email",
      "destinatario": "cliente@email.com",
      "asunto": "Actualización de investigación OF-2026-001",
      "contenido": "Se ha registrado un avistamiento...",
      "enviada": true,
      "fecha_envio": "2026-02-04T15:30:00Z",
      "intentos": 1,
      "error_mensaje": null,
      "created_at": "2026-02-04T15:30:00Z"
    }
  ],
  "total": 1
}
```

---

### `POST /notificaciones/oficios/{oficio_id}/notificaciones` - Enviar

**Request Body:**
```json
{
  "tipo": "email",
  "destinatario": "cliente@email.com",
  "asunto": "Actualización de investigación",
  "contenido": "Se ha registrado un avistamiento del vehículo..."
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `tipo` | string | ✅ | Tipo de notificación (`email`) |
| `destinatario` | string | ✅ | Email del destinatario |
| `asunto` | string | ✅ | Asunto del email |
| `contenido` | string | ✅ | Contenido del mensaje |

---

## Endpoints No Registrados

Los siguientes endpoints existen en el código pero **NO están registrados** en `main.py`:

### Google Drive Integration

**Archivo:** `src/modules/oficios/presentation/routers/drive_webhook_router.py`

| Método | Path | Descripción | Estado |
|--------|------|-------------|--------|
| `POST` | `/oficios/drive/webhook` | Webhook de Google Drive | ⚠️ NO REGISTRADO |
| `POST` | `/oficios/drive/process` | Procesamiento manual | ⚠️ NO REGISTRADO |

**Nota:** El router `drive_webhook_router` no está exportado en `src/modules/oficios/presentation/routers/__init__.py` ni incluido en `main.py`. Si se requiere la integración con Google Drive, se debe:

1. Agregar al `__init__.py`:
```python
from .drive_webhook_router import router as drive_webhook_router
__all__ = ["oficio_router", "document_upload_router", "drive_webhook_router"]
```

2. Registrar en `main.py`:
```python
from src.modules.oficios.presentation.routers import drive_webhook_router
app.include_router(drive_webhook_router)
```

---

## Códigos de Error

### Códigos HTTP Comunes

| Código | Descripción | Causa típica |
|--------|-------------|--------------|
| `200` | OK | Operación exitosa |
| `201` | Created | Recurso creado |
| `202` | Accepted | Proceso en background iniciado |
| `204` | No Content | Eliminación exitosa |
| `400` | Bad Request | Datos inválidos |
| `401` | Unauthorized | Token inválido o ausente |
| `403` | Forbidden | Sin permisos suficientes |
| `404` | Not Found | Recurso no existe |
| `409` | Conflict | Recurso duplicado |
| `429` | Too Many Requests | Rate limit excedido |
| `500` | Internal Server Error | Error del servidor |
| `502` | Bad Gateway | Error en servicio externo |
| `503` | Service Unavailable | Servicio deshabilitado |

### Formato de Error

```json
{
  "detail": "Descripción del error"
}
```

O con código:
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Error interno del servidor"
  }
}
```

---

## Observaciones y Pendientes

### Funcionalidades Implementadas ✅

1. **Autenticación completa** con JWT y roles
2. **CRUD de Buffets** con soft delete
3. **Gestión de Oficios** con vehículos, propietarios y direcciones
4. **Sistema de visitas** con registro de coordenadas GPS
5. **Timeline de investigaciones** con actividades y avistamientos
6. **Integración Boostr API** para consultas por RUT
7. **Sistema de notificaciones** por email
8. **Subida masiva de documentos** con procesamiento en background

### Pendientes / A Verificar 🔍

1. **Google Drive Integration**: Router existe pero no está registrado
2. **Health Check DB**: El endpoint `/health` tiene un TODO para verificar conexión real a BD
3. **Procesamiento Celery**: Los tasks están preparados para Celery pero pueden ejecutarse síncronamente
4. **Email Service**: Actualmente usa `MockEmailService` (verificar configuración producción)

### Mejoras Sugeridas 📝

1. Implementar endpoint `GET /usuarios/{id}` para obtener usuario por ID
2. Implementar endpoint `DELETE /usuarios/{id}` para desactivar usuario
3. Agregar endpoint para actualizar estado de documentos procesados
4. Implementar paginación en historial de visitas
5. Agregar filtros de fecha en timeline

---

## Changelog

| Fecha | Versión | Descripción |
|-------|---------|-------------|
| 2026-02-04 | 1.0.0 | Documentación inicial completa |

---

*Documentación generada automáticamente a partir del código fuente.*
