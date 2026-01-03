# Documentación de API

Documentación detallada de los endpoints de la API.

## 🔐 Autenticación

La API usa **JWT Bearer tokens** para autenticación.

### Obtener Token

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@sistema.com&password=admin123
```

**Respuesta**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Usar Token

Incluir en header `Authorization`:

```http
Authorization: Bearer <token>
```

## 👤 Usuarios y Autenticación

### Registrar Usuario

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "password123",
  "nombre": "Juan Perez",
  "rol": "cliente",
  "buffet_id": 1
}
```

**Roles disponibles**: `admin`, `investigador`, `cliente`

### Login (JSON)

```http
POST /api/v1/auth/login/json
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "password123"
}
```

### Obtener Usuario Actual

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

## 🏢 Buffets

### Listar Buffets

```http
GET /api/v1/buffets?skip=0&limit=20&activo_only=true
Authorization: Bearer <token>
```

### Crear Buffet

```http
POST /api/v1/buffets
Authorization: Bearer <token>
Content-Type: application/json

{
  "nombre": "Estudio Jurídico ABC",
  "rut": "12345678-5",
  "email_principal": "contacto@estudio.com",
  "telefono": "+56912345678",
  "contacto_nombre": "Juan Perez"
}
```

### Obtener Buffet

```http
GET /api/v1/buffets/{id}
Authorization: Bearer <token>
```

### Actualizar Buffet

```http
PUT /api/v1/buffets/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "nombre": "Nombre Actualizado",
  "telefono": "+56987654321"
}
```

### Eliminar Buffet (Soft Delete)

```http
DELETE /api/v1/buffets/{id}
Authorization: Bearer <token>
```

## 📋 Oficios

### Listar Oficios

```http
GET /api/v1/oficios?skip=0&limit=20&buffet_id=1&estado=pendiente
Authorization: Bearer <token>
```

**Filtros disponibles**:
- `buffet_id`: Filtrar por buffet
- `investigador_id`: Filtrar por investigador asignado
- `estado`: `pendiente`, `investigacion`, `notificacion`, `finalizado_encontrado`, `finalizado_no_encontrado`

### Crear Oficio

```http
POST /api/v1/oficios
Authorization: Bearer <token>
Content-Type: application/json

{
  "numero_oficio": "OF-2024-001",
  "buffet_id": 1,
  "vehiculo": {
    "patente": "ABCD12",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "color": "Blanco",
    "vin": "1HGBH41JXMN109186"
  },
  "prioridad": "media",
  "fecha_limite": "2024-12-31",
  "notas_generales": "Caso urgente",
  "propietarios": [
    {
      "rut": "12345678-9",
      "nombre_completo": "Juan Perez",
      "email": "juan@ejemplo.com",
      "telefono": "+56912345678",
      "tipo": "principal"
    }
  ],
  "direcciones": [
    {
      "direccion": "Av. Providencia 1234",
      "comuna": "Providencia",
      "region": "Metropolitana",
      "tipo": "domicilio"
    }
  ]
}
```

### Obtener Oficio

```http
GET /api/v1/oficios/{id}
Authorization: Bearer <token>
```

**Respuesta incluye**:
- Datos del oficio
- Vehículo asociado
- Propietarios
- Direcciones
- Timeline de actividades

### Agregar Propietario

```http
POST /api/v1/oficios/{id}/propietarios
Authorization: Bearer <token>
Content-Type: application/json

{
  "rut": "98765432-1",
  "nombre_completo": "Maria Lopez",
  "tipo": "codeudor",
  "email": "maria@ejemplo.com"
}
```

### Agregar Dirección

```http
POST /api/v1/oficios/{id}/direcciones
Authorization: Bearer <token>
Content-Type: application/json

{
  "direccion": "Av. Las Condes 5678",
  "comuna": "Las Condes",
  "region": "Metropolitana",
  "tipo": "trabajo",
  "notas": "Oficina principal"
}
```

## 🔍 Investigaciones

### Agregar Actividad

```http
POST /api/v1/investigaciones/oficios/{id}/actividades
Authorization: Bearer <token>
Content-Type: application/json

{
  "tipo_actividad": "nota",
  "descripcion": "Visita realizada a dirección registrada",
  "resultado": "No se encontró el vehículo",
  "api_externa": "boostr"
}
```

**Tipos de actividad**:
- `consulta_api`: Consulta a API externa
- `nota`: Nota del investigador
- `llamada`: Llamada telefónica
- `terreno`: Visita en terreno
- `otro`: Otro tipo

### Agregar Avistamiento

```http
POST /api/v1/investigaciones/oficios/{id}/avistamientos
Authorization: Bearer <token>
Content-Type: application/json

{
  "fuente": "terreno",
  "ubicacion": "Av. Providencia 1234, Providencia",
  "fecha_hora": "2024-01-15T10:30:00Z",
  "latitud": -33.4269,
  "longitud": -70.6150,
  "notas": "Vehículo estacionado frente al edificio"
}
```

**Fuentes disponibles**:
- `portico`: Pórtico de lectura
- `multa`: Multa asociada
- `terreno`: Avistamiento en terreno
- `otro`: Otra fuente

### Obtener Timeline

```http
GET /api/v1/investigaciones/oficios/{id}/timeline
Authorization: Bearer <token>
```

**Respuesta**:

```json
{
  "oficio_id": 1,
  "items": [
    {
      "tipo": "actividad",
      "id": 1,
      "fecha": "2024-01-15T10:30:00Z",
      "descripcion": "Visita realizada",
      "investigador_id": 2
    },
    {
      "tipo": "avistamiento",
      "id": 1,
      "fecha": "2024-01-14T15:20:00Z",
      "descripcion": "Avistamiento en terreno",
      "fuente": "terreno"
    }
  ],
  "total": 2
}
```

## 📧 Notificaciones

### Crear Notificación

```http
POST /api/v1/notificaciones/oficios/{id}/notificaciones
Authorization: Bearer <token>
Content-Type: application/json

{
  "tipo": "buffet",
  "destinatario": "cliente@ejemplo.com",
  "asunto": "Actualización de caso",
  "contenido": "Se ha encontrado el vehículo en la dirección registrada."
}
```

**Tipos disponibles**:
- `receptor_judicial`: Notificación a receptor judicial
- `buffet`: Notificación al buffet cliente
- `interna`: Notificación interna
- `otro`: Otro tipo

### Listar Notificaciones

```http
GET /api/v1/notificaciones/oficios/{id}/notificaciones
Authorization: Bearer <token>
```

## ⚠️ Códigos de Error

### 400 Bad Request

Datos inválidos en el request:

```json
{
  "detail": "Validation error: campo requerido"
}
```

### 401 Unauthorized

Token inválido o expirado:

```json
{
  "detail": "Token inválido o expirado"
}
```

### 403 Forbidden

Sin permisos para la acción:

```json
{
  "detail": "No tiene permisos para realizar esta acción"
}
```

### 404 Not Found

Recurso no encontrado:

```json
{
  "detail": "Oficio con ID 999 no encontrado"
}
```

### 409 Conflict

Conflicto (ej: email duplicado):

```json
{
  "detail": "El email 'usuario@ejemplo.com' ya está registrado"
}
```

### 500 Internal Server Error

Error interno del servidor:

```json
{
  "detail": "Error interno del servidor"
}
```

## 📝 Ejemplos

### Flujo Completo

1. **Login**:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}'
```

2. **Crear Buffet**:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/buffets" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Estudio ABC","rut":"12345678-5","email_principal":"contacto@estudio.com"}'
```

3. **Crear Oficio**:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/oficios" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"numero_oficio":"OF-2024-001","buffet_id":1,"vehiculo":{"patente":"ABCD12"}}'
```

4. **Agregar Actividad**:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/investigaciones/oficios/1/actividades" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"tipo_actividad":"nota","descripcion":"Visita realizada"}'
```

## 📚 Documentación Interactiva

Cuando el servidor está corriendo:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

