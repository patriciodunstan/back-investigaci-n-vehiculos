# 📚 Documentación Completa de API - Backend para Frontend

Documentación exhaustiva de todos los endpoints, DTOs, schemas y funcionalidades del backend para facilitar el desarrollo del frontend.

---

## 📋 Tabla de Contenidos

1. [Información General](#información-general)
2. [Autenticación](#autenticación)
3. [Módulo de Usuarios](#módulo-de-usuarios)
4. [Módulo de Buffets](#módulo-de-buffets)
5. [Módulo de Oficios](#módulo-de-oficios)
6. [Módulo de Investigaciones](#módulo-de-investigaciones)
7. [Módulo Boostr API](#módulo-boostr-api)
8. [Módulo de Notificaciones](#módulo-de-notificaciones)
9. [Endpoints de Sistema](#endpoints-de-sistema)
10. [Enums y Valores Válidos](#enums-y-valores-válidos)
11. [Manejo de Errores](#manejo-de-errores)
12. [Flujos de Trabajo](#flujos-de-trabajo)

---

## 🔗 Información General

### Base URL

```
Producción: https://tu-backend.onrender.com/api/v1
Desarrollo: http://127.0.0.1:8000/api/v1
```

### Autenticación

Todos los endpoints (excepto login y register) requieren autenticación mediante **JWT Bearer Token**.

**Header requerido:**
```http
Authorization: Bearer <token>
```

El token se obtiene mediante el endpoint de login y tiene una duración de **30 minutos** (1800 segundos).

### Headers Comunes

```http
Content-Type: application/json
Authorization: Bearer <token>
```

### Formato de Respuesta

Todas las respuestas exitosas devuelven JSON. Las fechas siguen el formato ISO 8601: `2024-01-15T12:00:00`.

### Paginación

Los endpoints que soportan paginación usan los siguientes query parameters:

- `skip`: Número de registros a saltar (default: 0)
- `limit`: Número máximo de registros a retornar (default: 20, max: 100)

---

## 🔐 Autenticación

### POST `/auth/register`

**Descripción:** Registra un nuevo usuario en el sistema.

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "password123",
  "nombre": "Juan Perez",
  "rol": "cliente",
  "buffet_id": 1
}
```

**Schema Request:**
- `email` (string, requerido): Email válido del usuario
- `password` (string, requerido): Contraseña mínimo 6 caracteres, máximo 100
- `nombre` (string, requerido): Nombre completo, mínimo 2 caracteres, máximo 255
- `rol` (enum, opcional): Rol del usuario (`admin`, `investigador`, `cliente`). Default: `cliente`
- `buffet_id` (integer, opcional): ID del buffet. Requerido solo para rol `cliente`

**Response (201 Created):**
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

**Códigos de Estado:**
- `201`: Usuario creado exitosamente
- `400`: Datos inválidos (validación fallida)
- `409`: Email ya existe

**Reglas de Negocio:**
- El email debe ser único en el sistema
- Si el rol es `cliente`, debe proporcionarse `buffet_id`
- Si el rol es `admin` o `investigador`, `buffet_id` debe ser `null`

---

### POST `/auth/login`

**Descripción:** Autentica un usuario usando OAuth2 form-data (estándar).

**Autenticación:** No requerida

**Content-Type:** `application/x-www-form-urlencoded`

**Request Body (form-data):**
```
username: admin@sistema.com
password: admin123
```

**Nota:** OAuth2 usa `username` para el email, no `email`.

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Códigos de Estado:**
- `200`: Login exitoso
- `401`: Credenciales incorrectas
- `403`: Usuario inactivo

---

### POST `/auth/login/json`

**Descripción:** Autentica un usuario usando JSON (recomendado para frontend).

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "admin@sistema.com",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Códigos de Estado:**
- `200`: Login exitoso
- `401`: Credenciales incorrectas
- `403`: Usuario inactivo

**Uso del Token:**
Guardar el `access_token` y enviarlo en el header `Authorization: Bearer <token>` en todas las peticiones subsiguientes.

---

### GET `/auth/me`

**Descripción:** Obtiene los datos del usuario autenticado.

**Autenticación:** Requerida

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "admin@test.com",
  "nombre": "Admin Sistema",
  "rol": "admin",
  "buffet_id": null,
  "activo": true,
  "avatar_url": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Códigos de Estado:**
- `200`: Datos obtenidos exitosamente
- `401`: Token inválido o expirado
- `403`: Usuario inactivo

---

## 👥 Módulo de Usuarios

Nota: El módulo de usuarios actualmente solo tiene endpoints de autenticación. Los endpoints de gestión de usuarios (listar, actualizar, etc.) no están implementados aún.

---

## 🏢 Módulo de Buffets

Base path: `/buffets`

### GET `/buffets`

**Descripción:** Lista todos los buffets con paginación y filtros.

**Autenticación:** Requerida

**Query Parameters:**
- `skip` (integer, opcional): Registros a saltar. Default: 0
- `limit` (integer, opcional): Máximo de registros. Default: 100, Max: 100
- `activo_only` (boolean, opcional): Solo mostrar activos. Default: `true`

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Estudio Jurídico ABC",
      "rut": "76123456-7",
      "email_principal": "contacto@abc.cl",
      "telefono": "+56912345678",
      "contacto_nombre": "Juan Perez",
      "token_tablero": "abc123token",
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

**Códigos de Estado:**
- `200`: Lista obtenida exitosamente
- `401`: No autenticado

---

### GET `/buffets/{buffet_id}`

**Descripción:** Obtiene un buffet específico por ID.

**Autenticación:** Requerida

**Path Parameters:**
- `buffet_id` (integer, requerido): ID del buffet

**Response (200 OK):**
```json
{
  "id": 1,
  "nombre": "Estudio Jurídico ABC",
  "rut": "76123456-7",
  "email_principal": "contacto@abc.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "Juan Perez",
  "token_tablero": "abc123token",
  "activo": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Códigos de Estado:**
- `200`: Buffet encontrado
- `401`: No autenticado
- `404`: Buffet no encontrado

---

### POST `/buffets`

**Descripción:** Crea un nuevo buffet.

**Autenticación:** Requerida (solo `admin`)

**Permisos:** Solo usuarios con rol `admin`

**Request Body:**
```json
{
  "nombre": "Estudio Jurídico ABC",
  "rut": "76123456-7",
  "email_principal": "contacto@abc.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "Juan Perez"
}
```

**Schema Request:**
- `nombre` (string, requerido): Nombre del buffet. Min: 2, Max: 255
- `rut` (string, requerido): RUT del buffet en formato chileno (ej: "76123456-7")
- `email_principal` (string, requerido): Email de contacto válido
- `telefono` (string, opcional): Teléfono. Max: 20
- `contacto_nombre` (string, opcional): Nombre de contacto. Max: 255

**Response (201 Created):**
```json
{
  "id": 1,
  "nombre": "Estudio Jurídico ABC",
  "rut": "76123456-7",
  "email_principal": "contacto@abc.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "Juan Perez",
  "token_tablero": "generated_token_here",
  "activo": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Nota:** El `token_tablero` se genera automáticamente al crear el buffet.

**Códigos de Estado:**
- `201`: Buffet creado exitosamente
- `400`: Datos inválidos
- `401`: No autenticado
- `403`: No tiene permisos (solo admin)
- `409`: RUT ya existe

---

### PUT `/buffets/{buffet_id}`

**Descripción:** Actualiza un buffet existente.

**Autenticación:** Requerida

**Path Parameters:**
- `buffet_id` (integer, requerido): ID del buffet

**Request Body:**
```json
{
  "nombre": "Nombre Actualizado",
  "email_principal": "nuevo@email.cl",
  "telefono": "+56987654321",
  "contacto_nombre": "Nuevo Contacto"
}
```

**Schema Request (todos los campos opcionales):**
- `nombre` (string, opcional): Min: 2, Max: 255
- `email_principal` (string, opcional): Email válido
- `telefono` (string, opcional): Max: 20
- `contacto_nombre` (string, opcional): Max: 255

**Nota:** El RUT no se puede actualizar.

**Response (200 OK):**
```json
{
  "id": 1,
  "nombre": "Nombre Actualizado",
  "rut": "76123456-7",
  "email_principal": "nuevo@email.cl",
  "telefono": "+56987654321",
  "contacto_nombre": "Nuevo Contacto",
  "token_tablero": "abc123token",
  "activo": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

**Códigos de Estado:**
- `200`: Buffet actualizado exitosamente
- `401`: No autenticado
- `404`: Buffet no encontrado

---

### DELETE `/buffets/{buffet_id}`

**Descripción:** Desactiva un buffet (soft delete).

**Autenticación:** Requerida (solo `admin`)

**Permisos:** Solo usuarios con rol `admin`

**Path Parameters:**
- `buffet_id` (integer, requerido): ID del buffet

**Response (204 No Content):**
Sin body.

**Códigos de Estado:**
- `204`: Buffet desactivado exitosamente
- `401`: No autenticado
- `403`: No tiene permisos (solo admin)
- `404`: Buffet no encontrado

**Nota:** Esta operación realiza un soft delete (marca `activo = false`), no elimina físicamente el registro.

---

## 📋 Módulo de Oficios

Base path: `/oficios`

### GET `/oficios`

**Descripción:** Lista oficios con filtros y paginación.

**Autenticación:** Requerida

**Query Parameters:**
- `skip` (integer, opcional): Default: 0
- `limit` (integer, opcional): Default: 20, Max: 100
- `buffet_id` (integer, opcional): Filtrar por buffet
- `investigador_id` (integer, opcional): Filtrar por investigador asignado
- `estado` (enum, opcional): Filtrar por estado (`pendiente`, `investigacion`, `notificacion`, `finalizado_encontrado`, `finalizado_no_encontrado`)

**Reglas de Filtrado:**
- Si el usuario es `cliente`, automáticamente se filtra por su `buffet_id`
- Los usuarios `admin` e `investigador` pueden ver todos los oficios

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "numero_oficio": "OF-2024-001",
      "buffet_id": 1,
      "buffet_nombre": "Estudio Jurídico ABC",
      "investigador_id": 2,
      "investigador_nombre": "Investigador 1",
      "estado": "investigacion",
      "prioridad": "media",
      "fecha_ingreso": "2024-01-15",
      "fecha_limite": "2024-02-15",
      "notas_generales": "Caso urgente",
      "vehiculos": [
        {
          "id": 1,
          "patente": "ABCD12",
          "marca": "Toyota",
          "modelo": "Corolla",
          "año": 2020,
          "color": "Blanco",
          "vin": "1HGBH41JXMN109186"
        }
      ],
      "propietarios": [
        {
          "id": 1,
          "rut": "12345678-9",
          "nombre_completo": "Juan Perez",
          "tipo": "principal",
          "email": "juan@email.com",
          "telefono": "+56912345678",
          "direccion_principal": "Av. Providencia 1234",
          "notas": null
        }
      ],
      "direcciones": [
        {
          "id": 1,
          "direccion": "Av. Providencia 1234, Providencia",
          "tipo": "domicilio",
          "comuna": "Providencia",
          "region": "Región Metropolitana",
          "verificada": false,
          "resultado_verificacion": "pendiente",
          "fecha_verificacion": null,
          "verificada_por_id": null,
          "verificada_por_nombre": null,
          "cantidad_visitas": 0,
          "notas": null
        }
      ],
      "created_at": "2024-01-15T00:00:00",
      "updated_at": "2024-01-15T12:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

**Códigos de Estado:**
- `200`: Lista obtenida exitosamente
- `401`: No autenticado

---

### GET `/oficios/{oficio_id}`

**Descripción:** Obtiene un oficio completo con todas sus relaciones (vehículos, propietarios, direcciones).

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Response (200 OK):**
Misma estructura que un item de la lista (ver GET `/oficios`).

**Códigos de Estado:**
- `200`: Oficio encontrado
- `401`: No autenticado
- `404`: Oficio no encontrado

---

### POST `/oficios`

**Descripción:** Crea un nuevo oficio con vehículo y opcionalmente propietarios y direcciones.

**Autenticación:** Requerida (solo `admin` o `investigador`)

**Permisos:** Solo usuarios con rol `admin` o `investigador`

**Request Body:**
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
    "vin": "1HGBH41JXMN109186"
  },
  "prioridad": "media",
  "fecha_limite": "2024-02-15",
  "notas_generales": "Caso urgente",
  "propietarios": [
    {
      "rut": "12345678-9",
      "nombre_completo": "Juan Perez",
      "tipo": "principal",
      "email": "juan@email.com",
      "telefono": "+56912345678",
      "direccion_principal": "Av. Providencia 1234",
      "notas": null
    }
  ],
  "direcciones": [
    {
      "direccion": "Av. Providencia 1234, Providencia",
      "tipo": "domicilio",
      "comuna": "Providencia",
      "region": "Región Metropolitana",
      "notas": null
    }
  ]
}
```

**Schema Request:**
- `numero_oficio` (string, requerido): Número único del oficio. Max: 50
- `buffet_id` (integer, requerido): ID del buffet solicitante
- `vehiculo` (object, requerido): Datos del vehículo
  - `patente` (string, requerido): Min: 6, Max: 10
  - `marca` (string, opcional): Max: 100
  - `modelo` (string, opcional): Max: 100
  - `año` (integer, opcional): Entre 1900 y 2100
  - `color` (string, opcional): Max: 50
  - `vin` (string, opcional): Max: 17
- `prioridad` (enum, opcional): `baja`, `media`, `alta`, `urgente`. Default: `media`
- `fecha_limite` (date, opcional): Fecha límite en formato YYYY-MM-DD
- `notas_generales` (string, opcional): Notas generales del oficio
- `propietarios` (array, opcional): Lista de propietarios
- `direcciones` (array, opcional): Lista de direcciones

**Response (201 Created):**
Oficio completo con todas las relaciones (ver GET `/oficios/{oficio_id}`).

**Códigos de Estado:**
- `201`: Oficio creado exitosamente
- `400`: Datos inválidos
- `401`: No autenticado
- `403`: No tiene permisos
- `409`: Número de oficio ya existe

---

### PUT `/oficios/{oficio_id}`

**Descripción:** Actualiza campos específicos de un oficio.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Request Body:**
```json
{
  "prioridad": "alta",
  "fecha_limite": "2024-02-20",
  "notas_generales": "Notas actualizadas"
}
```

**Schema Request (todos los campos opcionales):**
- `prioridad` (enum, opcional): `baja`, `media`, `alta`, `urgente`
- `fecha_limite` (date, opcional): Formato YYYY-MM-DD
- `notas_generales` (string, opcional)

**Response (200 OK):**
Oficio actualizado completo (ver GET `/oficios/{oficio_id}`).

**Códigos de Estado:**
- `200`: Oficio actualizado exitosamente
- `401`: No autenticado
- `404`: Oficio no encontrado

---

### PATCH `/oficios/{oficio_id}/asignar`

**Descripción:** Asigna un investigador a un oficio.

**Autenticación:** Requerida (solo `admin`)

**Permisos:** Solo usuarios con rol `admin`

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Request Body:**
```json
{
  "investigador_id": 2
}
```

**Schema Request:**
- `investigador_id` (integer, requerido): ID del usuario investigador

**Response (200 OK):**
Oficio actualizado con el investigador asignado.

**Códigos de Estado:**
- `200`: Investigador asignado exitosamente
- `401`: No autenticado
- `403`: No tiene permisos (solo admin)
- `404`: Oficio no encontrado

**Reglas de Negocio:**
- Al asignar un investigador, el estado cambia automáticamente a `investigacion` (si estaba en `pendiente`)

---

### PATCH `/oficios/{oficio_id}/estado`

**Descripción:** Cambia el estado de un oficio.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Request Body:**
```json
{
  "estado": "investigacion"
}
```

**Schema Request:**
- `estado` (enum, requerido): `pendiente`, `investigacion`, `notificacion`, `finalizado_encontrado`, `finalizado_no_encontrado`

**Response (200 OK):**
Oficio actualizado con el nuevo estado.

**Códigos de Estado:**
- `200`: Estado actualizado exitosamente
- `401`: No autenticado
- `404`: Oficio no encontrado

---

### POST `/oficios/{oficio_id}/propietarios`

**Descripción:** Agrega un propietario a un oficio existente.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Request Body:**
```json
{
  "rut": "12345678-9",
  "nombre_completo": "Juan Perez",
  "tipo": "principal",
  "email": "juan@email.com",
  "telefono": "+56912345678",
  "direccion_principal": "Av. Providencia 1234",
  "notas": null
}
```

**Schema Request:**
- `rut` (string, requerido): RUT del propietario
- `nombre_completo` (string, requerido): Max: 255
- `tipo` (enum, opcional): `principal`, `codeudor`, `aval`, `usuario`. Default: `principal`
- `email` (string, opcional): Email válido
- `telefono` (string, opcional): Max: 20
- `direccion_principal` (string, opcional): Max: 500
- `notas` (string, opcional)

**Response (201 Created):**
```json
{
  "id": 1,
  "rut": "12345678-9",
  "nombre_completo": "Juan Perez",
  "tipo": "principal",
  "email": "juan@email.com",
  "telefono": "+56912345678",
  "direccion_principal": "Av. Providencia 1234",
  "notas": null
}
```

**Códigos de Estado:**
- `201`: Propietario agregado exitosamente
- `401`: No autenticado
- `404`: Oficio no encontrado

---

### POST `/oficios/{oficio_id}/direcciones`

**Descripción:** Agrega una dirección a un oficio existente.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Request Body:**
```json
{
  "direccion": "Av. Providencia 1234, Providencia",
  "tipo": "domicilio",
  "comuna": "Providencia",
  "region": "Región Metropolitana",
  "notas": null
}
```

**Schema Request:**
- `direccion` (string, requerido): Dirección completa. Max: 500
- `tipo` (enum, opcional): `domicilio`, `trabajo`, `familiar`, `otro`. Default: `domicilio`
- `comuna` (string, opcional): Max: 100
- `region` (string, opcional): Max: 100
- `notas` (string, opcional)

**Response (201 Created):**
```json
{
  "id": 1,
  "direccion": "Av. Providencia 1234, Providencia",
  "tipo": "domicilio",
  "comuna": "Providencia",
  "region": "Región Metropolitana",
  "verificada": false,
  "resultado_verificacion": "pendiente",
  "fecha_verificacion": null,
  "verificada_por_id": null,
  "verificada_por_nombre": null,
  "cantidad_visitas": 0,
  "notas": null
}
```

**Códigos de Estado:**
- `201`: Dirección agregada exitosamente
- `401`: No autenticado
- `404`: Oficio no encontrado

**Nota:** La dirección se crea con `verificada = false` y `resultado_verificacion = "pendiente"`.

---

### POST `/oficios/direcciones/{direccion_id}/visitas`

**Descripción:** Registra una visita a una dirección y actualiza su estado de verificación.

**Autenticación:** Requerida

**Path Parameters:**
- `direccion_id` (integer, requerido): ID de la dirección

**Request Body:**
```json
{
  "resultado": "no_encontrado",
  "notas": "Se visitó a las 15:00, nadie respondió",
  "latitud": "-33.4489",
  "longitud": "-70.6693"
}
```

**Schema Request:**
- `resultado` (enum, requerido): 
  - `pendiente`: No ha sido visitada
  - `exitosa`: Se encontró al propietario/vehículo
  - `no_encontrado`: Nadie en el domicilio
  - `direccion_incorrecta`: La dirección no existe o es errónea
  - `se_mudo`: El propietario ya no vive ahí
  - `rechazo_atencion`: Se negaron a atender
  - `otro`: Otro resultado
- `notas` (string, opcional): Notas sobre la visita. Max: 2000
- `latitud` (string, opcional): Coordenada GPS. Max: 20
- `longitud` (string, opcional): Coordenada GPS. Max: 20

**Response (201 Created):**
```json
{
  "id": 1,
  "direccion_id": 1,
  "investigador_id": 2,
  "investigador_nombre": "Investigador 1",
  "fecha_visita": "2024-01-15T15:00:00",
  "resultado": "no_encontrado",
  "notas": "Se visitó a las 15:00, nadie respondió",
  "latitud": "-33.4489",
  "longitud": "-70.6693"
}
```

**Códigos de Estado:**
- `201`: Visita registrada exitosamente
- `401`: No autenticado
- `404`: Dirección no encontrada

**Reglas de Negocio:**
- El `investigador_id` se toma del usuario autenticado
- Si el resultado es `exitosa`, la dirección se marca como `verificada = true`
- Se incrementa `cantidad_visitas` de la dirección

---

### GET `/oficios/direcciones/{direccion_id}/visitas`

**Descripción:** Obtiene el historial de visitas a una dirección.

**Autenticación:** Requerida

**Path Parameters:**
- `direccion_id` (integer, requerido): ID de la dirección

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "direccion_id": 1,
    "investigador_id": 2,
    "investigador_nombre": "Investigador 1",
    "fecha_visita": "2024-01-15T15:00:00",
    "resultado": "no_encontrado",
    "notas": "Se visitó a las 15:00, nadie respondió",
    "latitud": "-33.4489",
    "longitud": "-70.6693"
  }
]
```

**Códigos de Estado:**
- `200`: Historial obtenido exitosamente
- `401`: No autenticado
- `404`: Dirección no encontrada

**Nota:** Las visitas se retornan ordenadas por fecha (más reciente primero).

---

### GET `/oficios/{oficio_id}/direcciones/pendientes`

**Descripción:** Obtiene las direcciones de un oficio que requieren verificación.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "direccion": "Av. Providencia 1234, Providencia",
    "tipo": "domicilio",
    "comuna": "Providencia",
    "region": "Región Metropolitana",
    "verificada": false,
    "resultado_verificacion": "pendiente",
    "fecha_verificacion": null,
    "verificada_por_id": null,
    "verificada_por_nombre": null,
    "cantidad_visitas": 0,
    "notas": null
  }
]
```

**Códigos de Estado:**
- `200`: Direcciones obtenidas exitosamente
- `401`: No autenticado
- `404`: Oficio no encontrado

**Reglas de Negocio:**
Incluye direcciones que:
- Nunca han sido visitadas (`pendiente`)
- Tienen resultado `no_encontrado` (intentar de nuevo)
- Tienen resultado `rechazo_atencion` (intentar de nuevo)

---

## 🔍 Módulo de Investigaciones

Base path: `/investigaciones`

### GET `/investigaciones/oficios/{oficio_id}/timeline`

**Descripción:** Obtiene el timeline de un oficio con todas las actividades y avistamientos ordenados cronológicamente.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Query Parameters:**
- `limit` (integer, opcional): Máximo de items. Default: 50, Max: 200

**Response (200 OK):**
```json
{
  "oficio_id": 1,
  "items": [
    {
      "tipo": "actividad",
      "id": 1,
      "fecha": "2024-01-15T12:00:00",
      "descripcion": "Consulta API: Vehículo ABCD12",
      "detalle": "Vehículo: Toyota Corolla",
      "fuente": null,
      "investigador_id": 2
    },
    {
      "tipo": "avistamiento",
      "id": 1,
      "fecha": "2024-01-15T14:00:00",
      "descripcion": "Avistamiento en Av. Providencia 1234",
      "detalle": null,
      "fuente": "portico",
      "investigador_id": null
    }
  ],
  "total": 2
}
```

**Tipos de Items:**
- `actividad`: Actividades registradas manualmente o desde APIs
- `avistamiento`: Avistamientos del vehículo

**Códigos de Estado:**
- `200`: Timeline obtenido exitosamente
- `401`: No autenticado
- `404`: Oficio no encontrado

**Nota:** Los items se ordenan por fecha descendente (más reciente primero).

---

### POST `/investigaciones/oficios/{oficio_id}/actividades`

**Descripción:** Agrega una actividad al timeline de un oficio.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Request Body:**
```json
{
  "tipo_actividad": "nota",
  "descripcion": "Visita a dirección registrada",
  "resultado": "No se encontró el vehículo",
  "api_externa": null,
  "datos_json": null
}
```

**Schema Request:**
- `tipo_actividad` (enum, opcional): `consulta_api`, `nota`, `llamada`, `terreno`. Default: `nota`
- `descripcion` (string, requerido): Descripción de la actividad. Min: 5, Max: 2000
- `resultado` (string, opcional): Resultado de la actividad. Max: 2000
- `api_externa` (string, opcional): Nombre de la API externa si aplica. Max: 100
- `datos_json` (string, opcional): Datos adicionales en formato JSON

**Response (201 Created):**
```json
{
  "id": 1,
  "oficio_id": 1,
  "investigador_id": 2,
  "tipo_actividad": "nota",
  "descripcion": "Visita a dirección registrada",
  "resultado": "No se encontró el vehículo",
  "api_externa": null,
  "datos_json": null,
  "fecha_actividad": "2024-01-15T12:00:00",
  "created_at": "2024-01-15T12:00:00"
}
```

**Códigos de Estado:**
- `201`: Actividad agregada exitosamente
- `400`: Datos inválidos
- `401`: No autenticado
- `404`: Oficio no encontrado

**Reglas de Negocio:**
- El `investigador_id` se toma del usuario autenticado
- La `fecha_actividad` se establece automáticamente a la fecha/hora actual

---

### POST `/investigaciones/oficios/{oficio_id}/avistamientos`

**Descripción:** Registra un avistamiento del vehículo.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Request Body:**
```json
{
  "fuente": "terreno",
  "ubicacion": "Av. Providencia 1234, Providencia",
  "fecha_hora": "2024-01-15T14:00:00",
  "latitud": -33.4269,
  "longitud": -70.6150,
  "notas": "Vehículo estacionado frente al edificio"
}
```

**Schema Request:**
- `fuente` (enum, opcional): `portico`, `multa`, `terreno`. Default: `terreno`
- `ubicacion` (string, requerido): Ubicación del avistamiento. Min: 5, Max: 500
- `fecha_hora` (datetime, opcional): Fecha y hora del avistamiento. Si no se proporciona, usa la fecha/hora actual
- `latitud` (float, opcional): Coordenada GPS. Entre -90 y 90
- `longitud` (float, opcional): Coordenada GPS. Entre -180 y 180
- `notas` (string, opcional): Notas adicionales. Max: 1000

**Response (201 Created):**
```json
{
  "id": 1,
  "oficio_id": 1,
  "fuente": "terreno",
  "fecha_hora": "2024-01-15T14:00:00",
  "ubicacion": "Av. Providencia 1234, Providencia",
  "latitud": -33.4269,
  "longitud": -70.6150,
  "api_response_id": null,
  "datos_json": null,
  "notas": "Vehículo estacionado frente al edificio",
  "created_at": "2024-01-15T14:00:00"
}
```

**Códigos de Estado:**
- `201`: Avistamiento registrado exitosamente
- `400`: Datos inválidos
- `401`: No autenticado
- `404`: Oficio no encontrado

---

## 🚗 Módulo Boostr API

Base path: `/boostr`

Este módulo permite consultar información de vehículos y personas a través de la API externa de Boostr Chile.

**Nota:** Todas las consultas consumen créditos de Boostr. El sistema registra automáticamente las consultas en el timeline si se proporciona `oficio_id`.

### GET `/boostr/vehiculo/{patente}`

**Descripción:** Consulta información básica de un vehículo por patente.

**Autenticación:** Requerida

**Path Parameters:**
- `patente` (string, requerido): Patente del vehículo

**Response (200 OK):**
```json
{
  "patente": "ABCD12",
  "marca": "Toyota",
  "modelo": "Corolla",
  "año": 2020,
  "tipo": "Automóvil",
  "color": "Blanco",
  "vin": "1HGBH41JXMN109186",
  "combustible": "Gasolina",
  "kilometraje": null,
  "propietario_rut": "12345678-9",
  "propietario_nombre": "Juan Perez"
}
```

**Códigos de Estado:**
- `200`: Información obtenida exitosamente
- `401`: No autenticado
- `404`: Vehículo no encontrado
- `429`: Rate limit excedido
- `502`: Error en servicio externo

**Coste:** 1 crédito de Boostr

---

### GET `/boostr/vehiculo/{patente}/multas`

**Descripción:** Consulta las multas de tránsito de un vehículo.

**Autenticación:** Requerida

**Path Parameters:**
- `patente` (string, requerido): Patente del vehículo

**Response (200 OK):**
```json
[
  {
    "juzgado": "Juzgado de Policía Local de Providencia",
    "comuna": "Providencia",
    "rol": "C-1234-2023",
    "año": 2023,
    "fecha": "2023-06-15",
    "estado": "Pendiente",
    "monto": 25000.0
  }
]
```

**Códigos de Estado:**
- `200`: Multas obtenidas exitosamente
- `401`: No autenticado
- `429`: Rate limit excedido
- `502`: Error en servicio externo

**Coste:** 1 crédito de Boostr

---

### GET `/boostr/persona/{rut}`

**Descripción:** Consulta información de una persona por RUT.

**Autenticación:** Requerida

**Path Parameters:**
- `rut` (string, requerido): RUT de la persona (formato: "12345678-9")

**Response (200 OK):**
```json
{
  "rut": "12345678-9",
  "nombre": "Juan Perez",
  "nombres": "Juan",
  "apellido_paterno": "Perez",
  "apellido_materno": "Gonzalez",
  "genero": "M",
  "nacionalidad": "Chilena",
  "fecha_nacimiento": "1980-01-15",
  "edad": 44,
  "fallecido": false
}
```

**Códigos de Estado:**
- `200`: Información obtenida exitosamente
- `400`: RUT inválido
- `401`: No autenticado
- `404`: Persona no encontrada
- `429`: Rate limit excedido
- `502`: Error en servicio externo

**Coste:** 1 crédito de Boostr

---

### GET `/boostr/persona/{rut}/vehiculos`

**Descripción:** Consulta los vehículos registrados a nombre de una persona.

**Autenticación:** Requerida

**Path Parameters:**
- `rut` (string, requerido): RUT de la persona

**Response (200 OK):**
```json
[
  {
    "patente": "ABCD12",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "tipo": "Automóvil"
  }
]
```

**Códigos de Estado:**
- `200`: Vehículos obtenidos exitosamente
- `400`: RUT inválido
- `401`: No autenticado
- `429`: Rate limit excedido
- `502`: Error en servicio externo

**Coste:** 1 crédito de Boostr

---

### POST `/boostr/investigar/vehiculo/{patente}`

**Descripción:** Realiza una investigación completa de un vehículo (información + multas) y opcionalmente registra la consulta en el timeline de un oficio.

**Autenticación:** Requerida

**Path Parameters:**
- `patente` (string, requerido): Patente del vehículo

**Query Parameters:**
- `oficio_id` (integer, opcional): ID del oficio para registrar la actividad en el timeline
- `incluir_multas` (boolean, opcional): Incluir consulta de multas. Default: `true`

**Response (200 OK):**
```json
{
  "vehiculo": {
    "patente": "ABCD12",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "tipo": "Automóvil",
    "color": "Blanco",
    "vin": "1HGBH41JXMN109186",
    "combustible": "Gasolina",
    "kilometraje": null,
    "propietario_rut": "12345678-9",
    "propietario_nombre": "Juan Perez"
  },
  "multas": [
    {
      "juzgado": "Juzgado de Policía Local de Providencia",
      "comuna": "Providencia",
      "rol": "C-1234-2023",
      "año": 2023,
      "fecha": "2023-06-15",
      "estado": "Pendiente",
      "monto": 25000.0
    }
  ],
  "creditos_usados": 2,
  "fecha_consulta": "2024-01-15T12:00:00"
}
```

**Códigos de Estado:**
- `200`: Investigación completada exitosamente
- `401`: No autenticado
- `429`: Rate limit excedido
- `502`: Error en servicio externo

**Coste:** 1-2 créditos de Boostr (según opciones)

**Reglas de Negocio:**
- Si se proporciona `oficio_id`, se registra automáticamente una actividad en el timeline con tipo `consulta_api`
- El `investigador_id` de la actividad se toma del usuario autenticado

---

### POST `/boostr/investigar/propietario/{rut}`

**Descripción:** Realiza una investigación completa de un propietario (información + otros vehículos) y opcionalmente registra la consulta en el timeline de un oficio.

**Autenticación:** Requerida

**Path Parameters:**
- `rut` (string, requerido): RUT del propietario

**Query Parameters:**
- `oficio_id` (integer, opcional): ID del oficio para registrar la actividad en el timeline
- `incluir_vehiculos` (boolean, opcional): Incluir otros vehículos. Default: `true`

**Response (200 OK):**
```json
{
  "propietario": {
    "rut": "12345678-9",
    "nombre": "Juan Perez",
    "nombres": "Juan",
    "apellido_paterno": "Perez",
    "apellido_materno": "Gonzalez",
    "genero": "M",
    "nacionalidad": "Chilena",
    "fecha_nacimiento": "1980-01-15",
    "edad": 44,
    "fallecido": false
  },
  "vehiculos": [
    {
      "patente": "ABCD12",
      "marca": "Toyota",
      "modelo": "Corolla",
      "año": 2020,
      "tipo": "Automóvil"
    }
  ],
  "creditos_usados": 2,
  "fecha_consulta": "2024-01-15T12:00:00"
}
```

**Códigos de Estado:**
- `200`: Investigación completada exitosamente
- `400`: RUT inválido
- `401`: No autenticado
- `429`: Rate limit excedido
- `502`: Error en servicio externo

**Coste:** 1-2 créditos de Boostr (según opciones)

**Reglas de Negocio:**
- Si se proporciona `oficio_id`, se registra automáticamente una actividad en el timeline con tipo `consulta_api`
- El `investigador_id` de la actividad se toma del usuario autenticado

---

## 📧 Módulo de Notificaciones

Base path: `/notificaciones`

### GET `/notificaciones/oficios/{oficio_id}/notificaciones`

**Descripción:** Obtiene el historial de notificaciones enviadas para un oficio.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Response (200 OK):**
```json
{
  "oficio_id": 1,
  "items": [
    {
      "id": 1,
      "oficio_id": 1,
      "tipo": "buffet",
      "destinatario": "cliente@ejemplo.cl",
      "asunto": "Actualización de caso",
      "contenido": "Se ha encontrado el vehículo...",
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

**Códigos de Estado:**
- `200`: Notificaciones obtenidas exitosamente
- `401`: No autenticado
- `404`: Oficio no encontrado

**Nota:** Las notificaciones se ordenan por fecha de creación descendente (más reciente primero).

---

### POST `/notificaciones/oficios/{oficio_id}/notificaciones`

**Descripción:** Envía una notificación y la registra en el sistema.

**Autenticación:** Requerida

**Path Parameters:**
- `oficio_id` (integer, requerido): ID del oficio

**Request Body:**
```json
{
  "tipo": "buffet",
  "destinatario": "cliente@ejemplo.cl",
  "asunto": "Actualización de caso",
  "contenido": "Se ha encontrado el vehículo en Av. Providencia 1234."
}
```

**Schema Request:**
- `tipo` (enum, opcional): `receptor_judicial`, `buffet`, `interna`. Default: `buffet`
- `destinatario` (string, requerido): Email o identificador del destinatario. Min: 3, Max: 255
- `asunto` (string, opcional): Asunto del email. Max: 500
- `contenido` (string, opcional): Contenido del email. Max: 5000

**Response (201 Created):**
```json
{
  "id": 1,
  "oficio_id": 1,
  "tipo": "buffet",
  "destinatario": "cliente@ejemplo.cl",
  "asunto": "Actualización de caso",
  "contenido": "Se ha encontrado el vehículo en Av. Providencia 1234.",
  "enviada": true,
  "fecha_envio": "2024-01-15T12:00:00",
  "intentos": 1,
  "error_mensaje": null,
  "created_at": "2024-01-15T12:00:00"
}
```

**Códigos de Estado:**
- `201`: Notificación enviada y registrada exitosamente
- `400`: Datos inválidos
- `401`: No autenticado
- `404`: Oficio no encontrado

**Reglas de Negocio:**
- La notificación se envía inmediatamente (usando MockEmailService en desarrollo)
- Si el envío es exitoso, `enviada = true` y `fecha_envio` se establece
- Si falla el envío, `enviada = false` y `error_mensaje` contiene el error

**Nota:** En producción, el sistema usa un servicio de email real. En desarrollo/testing, se usa MockEmailService que siempre tiene éxito.

---

## 🌐 Endpoints de Sistema

### GET `/`

**Descripción:** Endpoint raíz de la API.

**Autenticación:** No requerida

**Response (200 OK):**
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

**Descripción:** Health check del sistema.

**Autenticación:** No requerida

**Response (200 OK):**
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "connected"
}
```

---

### GET `/info`

**Descripción:** Información del sistema y configuración.

**Autenticación:** No requerida

**Response (200 OK):**
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

### RolEnum

Roles de usuario en el sistema:

- `admin`: Administrador con acceso completo
- `investigador`: Puede gestionar oficios e investigaciones
- `cliente`: Solo puede ver oficios de su buffet (lectura)

---

### EstadoOficioEnum

Estados posibles de un oficio:

- `pendiente`: Recién ingresado, sin investigador asignado
- `investigacion`: En proceso de investigación
- `notificacion`: Esperando notificación al receptor judicial
- `finalizado_encontrado`: Vehículo encontrado
- `finalizado_no_encontrado`: No se encontró el vehículo

**Flujo típico:** `pendiente` → `investigacion` → `notificacion` → `finalizado_*`

---

### PrioridadEnum

Niveles de prioridad para oficios:

- `baja`: Prioridad baja
- `media`: Prioridad media (default)
- `alta`: Prioridad alta
- `urgente`: Prioridad urgente

---

### TipoPropietarioEnum

Tipos de propietario/relacionado con el vehículo:

- `principal`: Propietario principal
- `codeudor`: Codeudor solidario
- `aval`: Aval
- `usuario`: Familiar que usa el vehículo

---

### TipoDireccionEnum

Tipos de dirección:

- `domicilio`: Casa del propietario (default)
- `trabajo`: Lugar de trabajo
- `familiar`: Casa de familiar
- `otro`: Otra dirección

---

### ResultadoVerificacionEnum

Resultado de la verificación de una dirección en terreno:

- `pendiente`: No ha sido visitada (default)
- `exitosa`: Se encontró al propietario/vehículo
- `no_encontrado`: Nadie en el domicilio
- `direccion_incorrecta`: La dirección no existe o es errónea
- `se_mudo`: El propietario ya no vive ahí
- `rechazo_atencion`: Se negaron a atender
- `otro`: Otro resultado

---

### TipoActividadEnum

Tipos de actividad en la investigación (timeline):

- `consulta_api`: Consulta a API externa (Boostr, etc.)
- `nota`: Nota del investigador (default)
- `llamada`: Llamada telefónica
- `terreno`: Visita en terreno

---

### FuenteAvistamientoEnum

Fuentes de avistamientos del vehículo:

- `portico`: API de pórticos (Boostr, etc.)
- `multa`: API de multas de tránsito
- `terreno`: Registrado manualmente en terreno (default)

---

### TipoNotificacionEnum

Tipos de notificación:

- `receptor_judicial`: Email a receptor judicial
- `buffet`: Email a buffet cliente (default)
- `interna`: Notificación interna del sistema

---

## ⚠️ Manejo de Errores

### Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Operación exitosa sin contenido
- `400 Bad Request`: Datos inválidos o validación fallida
- `401 Unauthorized`: No autenticado o token inválido/expirado
- `403 Forbidden`: Autenticado pero sin permisos
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto (ej: email/RUT ya existe)
- `429 Too Many Requests`: Rate limit excedido (Boostr API)
- `500 Internal Server Error`: Error interno del servidor
- `502 Bad Gateway`: Error en servicio externo (Boostr API)

### Formato de Errores

**Error estándar (400, 401, 403, 404, 409):**
```json
{
  "detail": "Mensaje de error descriptivo"
}
```

**Ejemplo 400:**
```json
{
  "detail": "Email o contraseña incorrectos"
}
```

**Ejemplo 404:**
```json
{
  "detail": "Oficio no encontrado"
}
```

**Ejemplo 409:**
```json
{
  "detail": "El email ya está registrado"
}
```

### Errores de Validación

Cuando hay errores de validación de campos, FastAPI retorna un formato detallado:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 6 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Manejo de Tokens Expirados

Cuando un token JWT expira o es inválido:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer

{
  "detail": "Token inválido o expirado"
}
```

**Acción recomendada:** Redirigir al usuario al login para obtener un nuevo token.

---

## 🔄 Flujos de Trabajo

### Flujo 1: Crear y Gestionar un Oficio

1. **Login:**
   ```
   POST /auth/login/json
   → Obtener token
   ```

2. **Crear oficio:**
   ```
   POST /oficios
   → Oficio creado en estado "pendiente"
   ```

3. **Asignar investigador (admin):**
   ```
   PATCH /oficios/{id}/asignar
   → Estado cambia automáticamente a "investigacion"
   ```

4. **Agregar direcciones:**
   ```
   POST /oficios/{id}/direcciones
   → Direcciones agregadas con verificada=false
   ```

5. **Consultar información (Boostr):**
   ```
   POST /boostr/investigar/vehiculo/{patente}?oficio_id={id}
   → Información obtenida y registrada en timeline
   ```

6. **Registrar visitas:**
   ```
   POST /oficios/direcciones/{direccion_id}/visitas
   → Visita registrada, dirección actualizada
   ```

7. **Agregar actividades:**
   ```
   POST /investigaciones/oficios/{id}/actividades
   → Actividad agregada al timeline
   ```

8. **Cambiar estado:**
   ```
   PATCH /oficios/{id}/estado
   → Estado actualizado (ej: "notificacion")
   ```

9. **Enviar notificación:**
   ```
   POST /notificaciones/oficios/{id}/notificaciones
   → Notificación enviada y registrada
   ```

10. **Finalizar:**
    ```
    PATCH /oficios/{id}/estado
    → Estado: "finalizado_encontrado" o "finalizado_no_encontrado"
    ```

### Flujo 2: Consultar Timeline Completo

1. **Login**
2. **Obtener oficio:**
   ```
   GET /oficios/{id}
   → Datos completos del oficio
   ```
3. **Obtener timeline:**
   ```
   GET /investigaciones/oficios/{id}/timeline?limit=100
   → Timeline completo con actividades y avistamientos
   ```

### Flujo 3: Gestionar Direcciones Pendientes

1. **Login**
2. **Obtener direcciones pendientes:**
   ```
   GET /oficios/{id}/direcciones/pendientes
   → Lista de direcciones que requieren verificación
   ```
3. **Registrar visita:**
   ```
   POST /oficios/direcciones/{direccion_id}/visitas
   → Visita registrada con resultado
   ```
4. **Ver historial:**
   ```
   GET /oficios/direcciones/{direccion_id}/visitas
   → Historial completo de visitas
   ```

---

## 📝 Notas Adicionales

### Autenticación y Tokens

- Los tokens JWT tienen una duración de **30 minutos** (1800 segundos)
- El frontend debe manejar la expiración de tokens y redirigir al login cuando sea necesario
- Guardar el token en localStorage o sessionStorage después del login
- Incluir el token en el header `Authorization: Bearer <token>` en todas las peticiones

### Paginación

- Usar `skip` y `limit` para implementar paginación
- El backend retorna `total` para calcular el número total de páginas
- Limitar `limit` a 100 como máximo

### Filtrado por Rol

- Los usuarios `cliente` solo pueden ver oficios de su `buffet_id`
- Los usuarios `admin` e `investigador` pueden ver todos los oficios
- El backend aplica automáticamente estos filtros

### Fechas y Horas

- Todas las fechas se manejan en formato ISO 8601: `2024-01-15T12:00:00`
- Las fechas de tipo `date` (sin hora): `2024-01-15`
- El backend retorna todas las fechas en UTC

### Rate Limiting (Boostr)

- La API de Boostr tiene límites de velocidad
- Si se excede el rate limit, retorna `429 Too Many Requests`
- Esperar 1 minuto antes de reintentar

### Soft Delete

- Las operaciones DELETE en buffets realizan soft delete (marcan `activo = false`)
- Los registros no se eliminan físicamente de la base de datos
- Para listar solo activos, usar `activo_only=true` (default)

---

## 🔗 Referencias

- **Swagger UI:** `/docs` (solo en desarrollo)
- **ReDoc:** `/redoc` (solo en desarrollo)
- **OpenAPI JSON:** `/openapi.json` (solo en desarrollo)

---

**Última actualización:** Enero 2025  
**Versión de API:** v1  
**Versión del documento:** 1.0.0
