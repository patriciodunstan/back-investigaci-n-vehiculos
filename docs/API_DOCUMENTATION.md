# 📚 Documentación de API - Frontend

Documentación completa de todos los endpoints disponibles para implementar el frontend.

## 🔗 Información General

**Base URL:** `https://tu-backend.onrender.com/api/v1`

**Autenticación:** JWT Bearer Token

**Headers requeridos:**
```javascript
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <token>"
}
```

---

## 🔐 Autenticación (`/auth`)

### POST `/auth/register`
Registrar nuevo usuario.

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password123",
  "nombre": "Juan Perez",
  "rol": "cliente",
  "buffet_id": 1
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "nombre": "Juan Perez",
  "rol": "cliente",
  "buffet_id": 1,
  "activo": true,
  "avatar_url": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Errores:**
- `409`: Email ya existe
- `400`: Datos inválidos

---

### POST `/auth/login/json`
Login con JSON (recomendado para frontend).

**Request:**
```json
{
  "email": "admin@sistema.com",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errores:**
- `401`: Credenciales incorrectas
- `403`: Usuario inactivo

**Nota:** Guarda el `access_token` y úsalo en el header `Authorization: Bearer <token>`

---

### POST `/auth/login`
Login con form-data (OAuth2 estándar).

**Request (form-data):**
```
username: admin@sistema.com
password: admin123
```

**Response:** Igual que `/auth/login/json`

---

### GET `/auth/me`
Obtener usuario actual (requiere autenticación).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "admin@sistema.com",
  "nombre": "Administrador Sistema",
  "rol": "admin",
  "buffet_id": null,
  "activo": true,
  "avatar_url": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Errores:**
- `401`: Token inválido o expirado

---

## 🏢 Buffets (`/buffets`)

Todos los endpoints requieren autenticación.

### GET `/buffets`
Listar buffets con paginación.

**Query Parameters:**
- `skip` (int, default: 0): Número de registros a saltar
- `limit` (int, default: 100, max: 100): Número de registros a retornar
- `activo_only` (bool, default: true): Solo buffets activos

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Estudio Juridico ABC",
      "rut": "76123456-7",
      "email_principal": "contacto@abc.cl",
      "telefono": "+56912345678",
      "contacto_nombre": "Juan Perez",
      "token_tablero": "abc123...",
      "activo": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

---

### GET `/buffets/{buffet_id}`
Obtener buffet por ID.

**Response (200):**
```json
{
  "id": 1,
  "nombre": "Estudio Juridico ABC",
  "rut": "76123456-7",
  "email_principal": "contacto@abc.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "Juan Perez",
  "token_tablero": "abc123...",
  "activo": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Errores:**
- `404`: Buffet no encontrado

---

### POST `/buffets`
Crear nuevo buffet (solo admin).

**Request:**
```json
{
  "nombre": "Estudio Juridico ABC",
  "rut": "76123456-7",
  "email_principal": "contacto@abc.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "Juan Perez"
}
```

**Response (201):** BuffetResponse

**Errores:**
- `403`: Solo admin puede crear
- `409`: RUT ya existe
- `400`: Datos inválidos

---

### PUT `/buffets/{buffet_id}`
Actualizar buffet.

**Request:**
```json
{
  "nombre": "Nuevo Nombre",
  "email_principal": "nuevo@email.cl",
  "telefono": "+56987654321",
  "contacto_nombre": "Maria Lopez"
}
```

**Response (200):** BuffetResponse

**Errores:**
- `404`: Buffet no encontrado

---

### DELETE `/buffets/{buffet_id}`
Desactivar buffet (soft delete, solo admin).

**Response (204):** Sin contenido

**Errores:**
- `403`: Solo admin puede eliminar
- `404`: Buffet no encontrado

---

## 📋 Oficios (`/oficios`)

Todos los endpoints requieren autenticación.

### GET `/oficios`
Listar oficios con filtros.

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 20, max: 100)
- `buffet_id` (int, optional): Filtrar por buffet
- `investigador_id` (int, optional): Filtrar por investigador
- `estado` (string, optional): `pendiente`, `investigacion`, `notificacion`, `finalizado_encontrado`, `finalizado_no_encontrado`

**Nota:** Los clientes solo ven oficios de su buffet automáticamente.

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "numero_oficio": "OF-2024-001",
      "buffet_id": 1,
      "buffet_nombre": "Estudio ABC",
      "investigador_id": 2,
      "investigador_nombre": "Pedro Investigador",
      "estado": "investigacion",
      "prioridad": "media",
      "fecha_ingreso": "2024-01-15",
      "fecha_limite": "2024-02-15",
      "notas_generales": "Caso urgente",
      "vehiculo": {
        "id": 1,
        "patente": "ABCD12",
        "marca": "Toyota",
        "modelo": "Corolla",
        "año": 2020,
        "color": "Blanco",
        "vin": null
      },
      "propietarios": [
        {
          "id": 1,
          "rut": "12345678-9",
          "nombre_completo": "Juan Perez",
          "tipo": "principal",
          "email": "juan@email.cl",
          "telefono": "+56912345678",
          "direccion_principal": "Av. Providencia 123",
          "notas": null
        }
      ],
      "direcciones": [
        {
          "id": 1,
          "direccion": "Av. Providencia 123",
          "comuna": "Providencia",
          "region": "Metropolitana",
          "tipo": "domicilio",
          "verificada": false,
          "fecha_verificacion": null,
          "notas": null
        }
      ],
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

---

### GET `/oficios/{oficio_id}`
Obtener oficio completo por ID.

**Response (200):** OficioResponse (igual estructura que items en lista)

**Errores:**
- `404`: Oficio no encontrado

---

### POST `/oficios`
Crear nuevo oficio (admin o investigador).

**Request:**
```json
{
  "numero_oficio": "OF-2024-001",
  "buffet_id": 1,
  "vehiculo": {
    "patente": "ABCD12",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "color": "Blanco",
    "vin": null
  },
  "prioridad": "media",
  "fecha_limite": "2024-02-15",
  "notas_generales": "Caso urgente",
  "propietarios": [
    {
      "rut": "12345678-9",
      "nombre_completo": "Juan Perez",
      "tipo": "principal",
      "email": "juan@email.cl",
      "telefono": "+56912345678",
      "direccion_principal": "Av. Providencia 123",
      "notas": null
    }
  ],
  "direcciones": [
    {
      "direccion": "Av. Providencia 123",
      "comuna": "Providencia",
      "region": "Metropolitana",
      "tipo": "domicilio",
      "notas": null
    }
  ]
}
```

**Response (201):** OficioResponse

**Errores:**
- `403`: Sin permisos
- `409`: Número de oficio ya existe
- `400`: Datos inválidos

---

### PUT `/oficios/{oficio_id}`
Actualizar oficio.

**Request:**
```json
{
  "prioridad": "alta",
  "fecha_limite": "2024-02-20",
  "notas_generales": "Actualizado"
}
```

**Response (200):** OficioResponse

**Errores:**
- `404`: Oficio no encontrado

---

### PATCH `/oficios/{oficio_id}/asignar`
Asignar investigador (solo admin).

**Request:**
```json
{
  "investigador_id": 2
}
```

**Response (200):** OficioResponse

**Errores:**
- `403`: Solo admin puede asignar
- `404`: Oficio no encontrado

---

### PATCH `/oficios/{oficio_id}/estado`
Cambiar estado del oficio.

**Request:**
```json
{
  "estado": "investigacion"
}
```

**Valores válidos:** `pendiente`, `investigacion`, `notificacion`, `finalizado_encontrado`, `finalizado_no_encontrado`

**Response (200):** OficioResponse

**Errores:**
- `404`: Oficio no encontrado

---

### POST `/oficios/{oficio_id}/propietarios`
Agregar propietario al oficio.

**Request:**
```json
{
  "rut": "12345678-9",
  "nombre_completo": "Juan Perez",
  "tipo": "principal",
  "email": "juan@email.cl",
  "telefono": "+56912345678",
  "direccion_principal": "Av. Providencia 123",
  "notas": null
}
```

**Response (201):**
```json
{
  "id": 1,
  "rut": "12345678-9",
  "nombre_completo": "Juan Perez",
  "tipo": "principal",
  "email": "juan@email.cl",
  "telefono": "+56912345678",
  "direccion_principal": "Av. Providencia 123",
  "notas": null
}
```

**Errores:**
- `404`: Oficio no encontrado

---

### POST `/oficios/{oficio_id}/direcciones`
Agregar dirección al oficio.

**Request:**
```json
{
  "direccion": "Av. Providencia 123",
  "comuna": "Providencia",
  "region": "Metropolitana",
  "tipo": "domicilio",
  "notas": null
}
```

**Response (201):**
```json
{
  "id": 1,
  "direccion": "Av. Providencia 123",
  "comuna": "Providencia",
  "region": "Metropolitana",
  "tipo": "domicilio",
  "verificada": false,
  "fecha_verificacion": null,
  "notas": null
}
```

**Errores:**
- `404`: Oficio no encontrado

---

## 🔍 Investigaciones (`/oficios/{oficio_id}/...`)

Todos los endpoints requieren autenticación.

### GET `/oficios/{oficio_id}/timeline`
Obtener timeline de actividades y avistamientos.

**Query Parameters:**
- `limit` (int, default: 50, max: 200): Número máximo de items

**Response (200):**
```json
{
  "oficio_id": 1,
  "items": [
    {
      "tipo": "actividad",
      "id": 1,
      "fecha": "2024-01-15T10:30:00",
      "descripcion": "Visita a direccion registrada",
      "detalle": "No se encontro el vehiculo",
      "fuente": null,
      "investigador_id": 2
    },
    {
      "tipo": "avistamiento",
      "id": 1,
      "fecha": "2024-01-14T15:20:00",
      "descripcion": "Avistamiento en terreno",
      "detalle": "Av. Providencia 1234",
      "fuente": "terreno",
      "investigador_id": null
    }
  ],
  "total": 2
}
```

---

### POST `/oficios/{oficio_id}/actividades`
Agregar actividad al timeline.

**Request:**
```json
{
  "tipo_actividad": "nota",
  "descripcion": "Visita a direccion registrada",
  "resultado": "No se encontro el vehiculo",
  "api_externa": null,
  "datos_json": null
}
```

**Tipos válidos:** `consulta_api`, `nota`, `llamada`, `terreno`

**Response (201):**
```json
{
  "id": 1,
  "oficio_id": 1,
  "investigador_id": 2,
  "tipo_actividad": "nota",
  "descripcion": "Visita a direccion registrada",
  "resultado": "No se encontro el vehiculo",
  "api_externa": null,
  "datos_json": null,
  "fecha_actividad": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### POST `/oficios/{oficio_id}/avistamientos`
Registrar avistamiento del vehículo.

**Request:**
```json
{
  "fuente": "terreno",
  "ubicacion": "Av. Providencia 1234, Providencia",
  "fecha_hora": "2024-01-14T15:20:00",
  "latitud": -33.4269,
  "longitud": -70.6150,
  "notas": "Vehiculo estacionado frente al edificio"
}
```

**Fuentes válidas:** `portico`, `multa`, `terreno`

**Response (201):**
```json
{
  "id": 1,
  "oficio_id": 1,
  "fuente": "terreno",
  "fecha_hora": "2024-01-14T15:20:00",
  "ubicacion": "Av. Providencia 1234, Providencia",
  "latitud": -33.4269,
  "longitud": -70.6150,
  "api_response_id": null,
  "datos_json": null,
  "notas": "Vehiculo estacionado frente al edificio",
  "created_at": "2024-01-14T15:20:00"
}
```

---

## 📧 Notificaciones (`/oficios/{oficio_id}/notificaciones`)

Todos los endpoints requieren autenticación.

### GET `/oficios/{oficio_id}/notificaciones`
Obtener historial de notificaciones.

**Response (200):**
```json
{
  "oficio_id": 1,
  "items": [
    {
      "id": 1,
      "oficio_id": 1,
      "tipo": "buffet",
      "destinatario": "cliente@ejemplo.cl",
      "asunto": "Actualizacion de caso",
      "contenido": "Se ha encontrado el vehiculo...",
      "enviada": true,
      "fecha_envio": "2024-01-15T12:00:00",
      "intentos": 1,
      "error_mensaje": null,
      "created_at": "2024-01-15T12:00:00"
    }
  ],
  "total": 1
}
```

---

### POST `/oficios/{oficio_id}/notificaciones`
Enviar notificación.

**Request:**
```json
{
  "tipo": "buffet",
  "destinatario": "cliente@ejemplo.cl",
  "asunto": "Actualizacion de caso",
  "contenido": "Se ha encontrado el vehiculo..."
}
```

**Tipos válidos:** `receptor_judicial`, `buffet`, `interna`

**Response (201):**
```json
{
  "id": 1,
  "oficio_id": 1,
  "tipo": "buffet",
  "destinatario": "cliente@ejemplo.cl",
  "asunto": "Actualizacion de caso",
  "contenido": "Se ha encontrado el vehiculo...",
  "enviada": true,
  "fecha_envio": "2024-01-15T12:00:00",
  "intentos": 1,
  "error_mensaje": null,
  "created_at": "2024-01-15T12:00:00"
}
```

---

## 🌐 Endpoints de Sistema

### GET `/`
Información básica de la API.

**Response (200):**
```json
{
  "app": "Sistema de Investigaciones Vehiculares",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

---

### GET `/health`
Health check.

**Response (200):**
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "connected"
}
```

---

### GET `/info`
Información del sistema.

**Response (200):**
```json
{
  "app_name": "Sistema de Investigaciones Vehiculares",
  "version": "1.0.0",
  "environment": "production",
  "debug": false,
  "api_version": "v1"
}
```

---

## 📊 Enums y Valores Válidos

### Roles (`RolEnum`)
- `admin`: Administrador
- `investigador`: Investigador
- `cliente`: Cliente (buffet)

### Estados de Oficio (`EstadoOficioEnum`)
- `pendiente`: Recién ingresado
- `investigacion`: En proceso
- `notificacion`: Esperando notificación
- `finalizado_encontrado`: Vehículo encontrado
- `finalizado_no_encontrado`: No se encontró

### Prioridad (`PrioridadEnum`)
- `baja`
- `media`
- `alta`
- `urgente`

### Tipo de Propietario (`TipoPropietarioEnum`)
- `principal`: Propietario principal
- `codeudor`: Codeudor solidario
- `aval`: Aval
- `usuario`: Familiar que usa el vehículo

### Tipo de Dirección (`TipoDireccionEnum`)
- `domicilio`: Casa del propietario
- `trabajo`: Lugar de trabajo
- `familiar`: Casa de familiar
- `otro`: Otra dirección

### Tipo de Actividad (`TipoActividadEnum`)
- `consulta_api`: Consulta a API externa
- `nota`: Nota del investigador
- `llamada`: Llamada telefónica
- `terreno`: Visita en terreno

### Fuente de Avistamiento (`FuenteAvistamientoEnum`)
- `portico`: API de pórticos
- `multa`: API de multas
- `terreno`: Registrado manualmente

### Tipo de Notificación (`TipoNotificacionEnum`)
- `receptor_judicial`: Email a receptor judicial
- `buffet`: Email a buffet cliente
- `interna`: Notificación interna

---

## 🔒 Permisos por Rol

### Admin
- ✅ Acceso completo a todos los endpoints
- ✅ Crear/editar/eliminar buffets
- ✅ Asignar investigadores
- ✅ Ver todos los oficios

### Investigador
- ✅ Crear/editar oficios
- ✅ Agregar actividades y avistamientos
- ✅ Cambiar estado de oficios
- ✅ Ver oficios asignados

### Cliente
- ✅ Ver oficios de su buffet (solo lectura)
- ✅ Ver timeline de oficios
- ✅ Ver notificaciones
- ❌ No puede crear/editar oficios
- ❌ No puede asignar investigadores

---

## ⚠️ Códigos de Estado HTTP

- `200`: OK - Operación exitosa
- `201`: Created - Recurso creado
- `204`: No Content - Eliminación exitosa
- `400`: Bad Request - Datos inválidos
- `401`: Unauthorized - Token inválido o faltante
- `403`: Forbidden - Sin permisos
- `404`: Not Found - Recurso no encontrado
- `409`: Conflict - Recurso ya existe
- `500`: Internal Server Error - Error del servidor

---

## 💡 Ejemplos de Uso

### Ejemplo: Login y obtener usuario
```javascript
// 1. Login
const loginResponse = await fetch('https://api.ejemplo.com/api/v1/auth/login/json', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@sistema.com',
    password: 'admin123'
  })
});

const { access_token } = await loginResponse.json();

// 2. Obtener usuario actual
const userResponse = await fetch('https://api.ejemplo.com/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const user = await userResponse.json();
```

### Ejemplo: Listar oficios con filtros
```javascript
const response = await fetch(
  'https://api.ejemplo.com/api/v1/oficios?skip=0&limit=20&estado=investigacion',
  {
    headers: {
      'Authorization': `Bearer ${access_token}`
    }
  }
);

const { items, total } = await response.json();
```

### Ejemplo: Crear oficio
```javascript
const response = await fetch('https://api.ejemplo.com/api/v1/oficios', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    numero_oficio: 'OF-2024-001',
    buffet_id: 1,
    vehiculo: {
      patente: 'ABCD12',
      marca: 'Toyota',
      modelo: 'Corolla',
      año: 2020,
      color: 'Blanco'
    },
    prioridad: 'media',
    propietarios: [
      {
        rut: '12345678-9',
        nombre_completo: 'Juan Perez',
        tipo: 'principal'
      }
    ]
  })
});

const oficio = await response.json();
```

---

## 📝 Notas Importantes

1. **Token JWT**: Expira en 30 minutos (1800 segundos). Implementa refresh token si es necesario.

2. **Paginación**: Usa `skip` y `limit` para paginación. El máximo de `limit` varía por endpoint.

3. **Fechas**: Todas las fechas están en formato ISO 8601 (`YYYY-MM-DDTHH:mm:ss`).

4. **CORS**: Configurado para permitir todos los orígenes (`*`).

5. **Errores**: Siempre revisa el código de estado HTTP y el campo `detail` en respuestas de error.

6. **Cliente automático**: Los usuarios con rol `cliente` solo ven oficios de su `buffet_id` automáticamente.

---

## 🔗 Documentación Interactiva

Si el backend está en modo debug, puedes acceder a:
- **Swagger UI**: `https://tu-backend.onrender.com/docs`
- **ReDoc**: `https://tu-backend.onrender.com/redoc`

Estos endpoints proporcionan documentación interactiva con ejemplos y la posibilidad de probar los endpoints directamente.

