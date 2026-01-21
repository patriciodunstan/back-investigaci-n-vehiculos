# API Endpoints - Sistema de Investigaciones Vehiculares

**Base URL:** `https://investigaciones-backend.onrender.com`

**Versión:** 1.0.0

**Última actualización:** 2026-01-20

---

## Índice

1. [Sistema](#1-sistema)
2. [Autenticación](#2-autenticación)
3. [Usuarios](#3-usuarios)
4. [Buffets](#4-buffets)
5. [Oficios](#5-oficios)
6. [Investigaciones](#6-investigaciones)
7. [Boostr API](#7-boostr-api)
8. [Notificaciones](#8-notificaciones)
9. [Documentos](#9-documentos)

---

## 1. Sistema

### 1.1. Health Check

**GET** `/health`

Verifica el estado de la API.

**Response 200:**
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "connected"
}
```

### 1.2. Información del Sistema

**GET** `/info`

Retorna información general del sistema.

**Response 200:**
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

## 2. Autenticación

### 2.1. Registro de Usuario

**POST** `/auth/register`

Crea un nuevo usuario en el sistema.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "nombre": "Juan Pérez",
  "rol": "investigador",
  "buffet_id": 1
}
```

**Campos:**
- `email` (string, required): Email único del usuario
- `password` (string, required): Contraseña (mínimo 6 caracteres)
- `nombre` (string, required): Nombre completo
- `rol` (enum, required): `admin`, `investigador`, `cliente`
- `buffet_id` (integer, optional): ID del buffet (requerido para rol `cliente`)

**Response 201:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "nombre": "Juan Pérez",
  "rol": "investigador",
  "buffet_id": null,
  "activo": true,
  "avatar_url": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- `409 Conflict`: Email ya existe
- `400 Bad Request`: Datos inválidos

---

### 2.2. Login (Form Data)

**POST** `/auth/login`

Autentica un usuario y retorna token JWT.

**Request (Form Data):**
- `username`: Email del usuario
- `password`: Contraseña

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Errores:**
- `401 Unauthorized`: Credenciales incorrectas
- `403 Forbidden`: Usuario inactivo

---

### 2.3. Login (JSON)

**POST** `/auth/login/json`

Login alternativo usando JSON en lugar de form-data.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### 2.4. Usuario Actual

**GET** `/auth/me`

Obtiene los datos del usuario autenticado.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "nombre": "Juan Pérez",
  "rol": "investigador",
  "buffet_id": null,
  "activo": true,
  "avatar_url": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## 3. Usuarios

### 3.1. Listar Usuarios

**GET** `/usuarios`

Obtiene una lista paginada de usuarios del sistema.

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `skip` (integer, default: 0): Registros a saltar (paginación)
- `limit` (integer, default: 100, max: 100): Máximo de registros
- `activo_only` (boolean, default: true): Solo usuarios activos
- `rol` (enum, optional): Filtrar por rol (`admin`, `investigador`, `cliente`)
- `buffet_id` (integer, optional): Filtrar por buffet

**Response 200:**
```json
{
  "items": [
    {
      "id": 1,
      "email": "user@example.com",
      "nombre": "Juan Pérez",
      "rol": "investigador",
      "buffet_id": null,
      "activo": true,
      "avatar_url": null,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 100
}
```

---

## 4. Buffets

### 4.1. Listar Buffets

**GET** `/buffets`

Lista todos los buffets con paginación.

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `skip` (integer, default: 0)
- `limit` (integer, default: 100, max: 100)
- `activo_only` (boolean, default: true)

**Response 200:**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Buffet Pérez & Asociados",
      "rut": "76123456-7",
      "email_principal": "contacto@buffet.cl",
      "telefono": "+56912345678",
      "contacto_nombre": "María Pérez",
      "token_tablero": "abc123def456",
      "activo": true,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-10T08:00:00Z"
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 100
}
```

---

### 4.2. Obtener Buffet

**GET** `/buffets/{buffet_id}`

Obtiene un buffet por ID.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "id": 1,
  "nombre": "Buffet Pérez & Asociados",
  "rut": "76123456-7",
  "email_principal": "contacto@buffet.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "María Pérez",
  "token_tablero": "abc123def456",
  "activo": true,
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-10T08:00:00Z"
}
```

**Errores:**
- `404 Not Found`: Buffet no encontrado

---

### 4.3. Crear Buffet

**POST** `/buffets`

Crea un nuevo buffet. **Solo administradores.**

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "nombre": "Buffet Pérez & Asociados",
  "rut": "76123456-7",
  "email_principal": "contacto@buffet.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "María Pérez"
}
```

**Response 201:**
```json
{
  "id": 1,
  "nombre": "Buffet Pérez & Asociados",
  "rut": "76123456-7",
  "email_principal": "contacto@buffet.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "María Pérez",
  "token_tablero": "abc123def456",
  "activo": true,
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-10T08:00:00Z"
}
```

**Errores:**
- `403 Forbidden`: No es administrador
- `409 Conflict`: RUT ya existe

---

### 4.4. Actualizar Buffet

**PUT** `/buffets/{buffet_id}`

Actualiza un buffet existente.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "nombre": "Buffet Pérez & Asociados S.A.",
  "email_principal": "contacto@buffet.cl",
  "telefono": "+56912345678",
  "contacto_nombre": "María Pérez"
}
```

**Response 200:** (mismo formato que crear)

---

### 4.5. Eliminar Buffet

**DELETE** `/buffets/{buffet_id}`

Desactiva un buffet (soft delete). **Solo administradores.**

**Headers:**
```
Authorization: Bearer {token}
```

**Response 204:** No Content

---

## 5. Oficios

### 5.1. Listar Oficios

**GET** `/oficios`

Lista oficios con filtros.

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `skip` (integer, default: 0)
- `limit` (integer, default: 20, max: 100)
- `buffet_id` (integer, optional): Filtrar por buffet
- `investigador_id` (integer, optional): Filtrar por investigador
- `estado` (enum, optional): `pendiente`, `asignado`, `en_progreso`, `completado`, `archivado`

**Response 200:**
```json
{
  "items": [
    {
      "id": 1,
      "numero_oficio": "OF-2024-001",
      "buffet_id": 1,
      "buffet_nombre": "Buffet Pérez",
      "investigador_id": 2,
      "investigador_nombre": "Juan Investigador",
      "estado": "en_progreso",
      "prioridad": "alta",
      "fecha_ingreso": "2024-01-15",
      "fecha_limite": "2024-02-15",
      "notas_generales": "Caso urgente",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z",
      "vehiculos": [
        {
          "id": 1,
          "patente": "ABCD12",
          "marca": "Toyota",
          "modelo": "Corolla",
          "año": 2020,
          "color": "Blanco",
          "vin": "JTD123456789"
        }
      ],
      "propietarios": [
        {
          "id": 1,
          "rut": "12345678-9",
          "nombre_completo": "Pedro González",
          "tipo": "natural",
          "email": "pedro@example.com",
          "telefono": "+56912345678",
          "direccion_principal": "Av. Principal 123",
          "notas": null
        }
      ],
      "direcciones": [
        {
          "id": 1,
          "direccion": "Av. Principal 123",
          "tipo": "domicilio",
          "comuna": "Santiago",
          "region": "Metropolitana",
          "verificada": false,
          "fecha_verificacion": null,
          "notas": null
        }
      ]
    }
  ],
  "total": 45,
  "skip": 0,
  "limit": 20
}
```

---

### 5.2. Obtener Oficio

**GET** `/oficios/{oficio_id}`

Obtiene un oficio con todas sus relaciones.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:** (mismo formato que item de lista)

---

### 5.3. Crear Oficio

**POST** `/oficios`

Crea un nuevo oficio con vehículo. **Solo admin o investigador.**

**Headers:**
```
Authorization: Bearer {token}
```

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
    "vin": "JTD123456789"
  },
  "prioridad": "alta",
  "fecha_limite": "2024-02-15",
  "notas_generales": "Caso urgente",
  "propietarios": [
    {
      "rut": "12345678-9",
      "nombre_completo": "Pedro González",
      "tipo": "natural",
      "email": "pedro@example.com",
      "telefono": "+56912345678",
      "direccion_principal": "Av. Principal 123",
      "notas": null
    }
  ],
  "direcciones": [
    {
      "direccion": "Av. Principal 123",
      "comuna": "Santiago",
      "region": "Metropolitana",
      "tipo": "domicilio",
      "notas": null
    }
  ]
}
```

**Campos opcionales:**
- `propietarios` (array, optional)
- `direcciones` (array, optional)
- `notas_generales` (string, optional)

**Response 201:** (mismo formato que GET)

**Errores:**
- `403 Forbidden`: No tiene permisos
- `409 Conflict`: Número de oficio ya existe

---

### 5.4. Actualizar Oficio

**PUT** `/oficios/{oficio_id}`

Actualiza un oficio.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "prioridad": "media",
  "fecha_limite": "2024-03-15",
  "notas_generales": "Actualización de notas"
}
```

**Response 200:** (mismo formato que GET)

---

### 5.5. Asignar Investigador

**PATCH** `/oficios/{oficio_id}/asignar`

Asigna un investigador al oficio. **Solo admin.**

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "investigador_id": 2
}
```

**Response 200:** (mismo formato que GET)

---

### 5.6. Cambiar Estado

**PATCH** `/oficios/{oficio_id}/estado`

Cambia el estado del oficio.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "estado": "completado"
}
```

**Valores de estado:**
- `pendiente`
- `asignado`
- `en_progreso`
- `completado`
- `archivado`

**Response 200:** (mismo formato que GET)

---

### 5.7. Agregar Propietario

**POST** `/oficios/{oficio_id}/propietarios`

Agrega un propietario al oficio.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "rut": "12345678-9",
  "nombre_completo": "Pedro González",
  "tipo": "natural",
  "email": "pedro@example.com",
  "telefono": "+56912345678",
  "direccion_principal": "Av. Principal 123",
  "notas": "Propietario adicional"
}
```

**Tipos de propietario:**
- `natural`: Persona natural
- `juridica`: Persona jurídica

**Response 201:**
```json
{
  "id": 1,
  "rut": "12345678-9",
  "nombre_completo": "Pedro González",
  "tipo": "natural",
  "email": "pedro@example.com",
  "telefono": "+56912345678",
  "direccion_principal": "Av. Principal 123",
  "notas": "Propietario adicional"
}
```

---

### 5.8. Agregar Dirección

**POST** `/oficios/{oficio_id}/direcciones`

Agrega una dirección al oficio.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "direccion": "Calle Falsa 123",
  "tipo": "trabajo",
  "comuna": "Providencia",
  "region": "Metropolitana",
  "notas": "Oficina principal"
}
```

**Tipos de dirección:**
- `domicilio`: Domicilio principal
- `trabajo`: Lugar de trabajo
- `alternativa`: Dirección alternativa

**Response 201:**
```json
{
  "id": 2,
  "direccion": "Calle Falsa 123",
  "tipo": "trabajo",
  "comuna": "Providencia",
  "region": "Metropolitana",
  "verificada": false,
  "resultado_verificacion": null,
  "fecha_verificacion": null,
  "verificada_por_id": null,
  "verificada_por_nombre": null,
  "cantidad_visitas": 0,
  "notas": "Oficina principal"
}
```

---

### 5.9. Registrar Visita a Dirección

**POST** `/oficios/direcciones/{direccion_id}/visitas`

Registra una visita a una dirección.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "resultado": "exitosa",
  "notas": "Se encontró al propietario",
  "latitud": -33.4489,
  "longitud": -70.6693
}
```

**Resultados posibles:**
- `exitosa`: Se encontró al propietario/vehículo
- `no_encontrado`: Nadie en el domicilio
- `direccion_incorrecta`: La dirección no existe
- `se_mudo`: El propietario ya no vive ahí
- `rechazo_atencion`: Se negaron a atender
- `otro`: Otro resultado

**Response 201:**
```json
{
  "id": 1,
  "direccion_id": 2,
  "investigador_id": 2,
  "investigador_nombre": "Juan Investigador",
  "fecha_visita": "2024-01-15T14:30:00Z",
  "resultado": "exitosa",
  "notas": "Se encontró al propietario",
  "latitud": -33.4489,
  "longitud": -70.6693
}
```

---

### 5.10. Historial de Visitas

**GET** `/oficios/direcciones/{direccion_id}/visitas`

Obtiene el historial de visitas a una dirección.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
[
  {
    "id": 1,
    "direccion_id": 2,
    "investigador_id": 2,
    "investigador_nombre": "Juan Investigador",
    "fecha_visita": "2024-01-15T14:30:00Z",
    "resultado": "exitosa",
    "notas": "Se encontró al propietario",
    "latitud": -33.4489,
    "longitud": -70.6693
  }
]
```

---

### 5.11. Direcciones Pendientes

**GET** `/oficios/{oficio_id}/direcciones/pendientes`

Obtiene direcciones de un oficio que requieren verificación.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
[
  {
    "id": 1,
    "direccion": "Av. Principal 123",
    "tipo": "domicilio",
    "comuna": "Santiago",
    "region": "Metropolitana",
    "verificada": false,
    "resultado_verificacion": null,
    "fecha_verificacion": null,
    "verificada_por_id": null,
    "verificada_por_nombre": null,
    "cantidad_visitas": 0,
    "notas": null
  }
]
```

---

## 6. Investigaciones

### 6.1. Obtener Timeline

**GET** `/investigaciones/oficios/{oficio_id}/timeline`

Obtiene el timeline de un oficio con actividades y avistamientos.

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `limit` (integer, default: 50, max: 200)

**Response 200:**
```json
{
  "oficio_id": 1,
  "items": [
    {
      "tipo": "actividad",
      "id": 1,
      "fecha": "2024-01-15T10:00:00Z",
      "descripcion": "Consulta Boostr: Vehículo ABCD12",
      "detalle": "Vehículo: Toyota Corolla",
      "fuente": "boostr",
      "investigador_id": 2
    },
    {
      "tipo": "avistamiento",
      "id": 1,
      "fecha": "2024-01-14T15:30:00Z",
      "descripcion": "Avistamiento en Providencia",
      "detalle": "Vehículo visto en Av. Providencia",
      "fuente": "testigo",
      "investigador_id": null
    }
  ],
  "total": 2
}
```

---

### 6.2. Agregar Actividad

**POST** `/investigaciones/oficios/{oficio_id}/actividades`

Agrega una actividad al timeline.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "tipo_actividad": "llamada",
  "descripcion": "Llamada al propietario",
  "resultado": "No contestó",
  "api_externa": null,
  "datos_json": null
}
```

**Tipos de actividad:**
- `llamada`: Llamada telefónica
- `visita`: Visita presencial
- `email`: Correo electrónico
- `consulta_api`: Consulta a API externa
- `otro`: Otra actividad

**Response 201:**
```json
{
  "id": 1,
  "oficio_id": 1,
  "investigador_id": 2,
  "tipo_actividad": "llamada",
  "descripcion": "Llamada al propietario",
  "resultado": "No contestó",
  "api_externa": null,
  "datos_json": null,
  "fecha_actividad": "2024-01-15T10:00:00Z",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### 6.3. Registrar Avistamiento

**POST** `/investigaciones/oficios/{oficio_id}/avistamientos`

Registra un avistamiento del vehículo.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "fuente": "testigo",
  "ubicacion": "Av. Providencia 1234",
  "fecha_hora": "2024-01-14T15:30:00Z",
  "latitud": -33.4489,
  "longitud": -70.6693,
  "notas": "Visto estacionado"
}
```

**Response 201:**
```json
{
  "id": 1,
  "oficio_id": 1,
  "fuente": "testigo",
  "fecha_hora": "2024-01-14T15:30:00Z",
  "ubicacion": "Av. Providencia 1234",
  "latitud": -33.4489,
  "longitud": -70.6693,
  "api_response_id": null,
  "datos_json": null,
  "notas": "Visto estacionado",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## 7. Boostr API

### 7.1. Consultar Vehículo por Patente

**GET** `/boostr/vehiculo/{patente}`

Consulta información de un vehículo por su patente.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "patente": "ABCD12",
  "marca": "Toyota",
  "modelo": "Corolla",
  "año": 2020,
  "tipo": "Automóvil",
  "color": "Blanco",
  "vin": "JTD123456789",
  "combustible": "Gasolina",
  "kilometraje": 50000,
  "propietario_rut": "12345678-9",
  "propietario_nombre": "Pedro González"
}
```

**Consume 1 crédito de Boostr.**

**Errores:**
- `404 Not Found`: Vehículo no encontrado
- `429 Too Many Requests`: Rate limit excedido
- `502 Bad Gateway`: Error en servicio externo

---

### 7.2. Consultar Multas de Vehículo

**GET** `/boostr/vehiculo/{patente}/multas`

Consulta las multas de tránsito de un vehículo.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
[
  {
    "juzgado": "Juzgado de Policía Local de Santiago",
    "comuna": "Santiago",
    "rol": "12345-2023",
    "año": 2023,
    "fecha": "2023-05-15",
    "estado": "Pendiente",
    "monto": 50000.0
  }
]
```

**Consume 1 crédito de Boostr.**

---

### 7.3. Consultar Persona por RUT

**GET** `/boostr/persona/{rut}`

Consulta información de una persona por su RUT.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "rut": "12345678-9",
  "nombre": "Pedro González Pérez",
  "nombres": "Pedro",
  "apellido_paterno": "González",
  "apellido_materno": "Pérez",
  "genero": "M",
  "nacionalidad": "Chilena",
  "fecha_nacimiento": "1985-03-15",
  "edad": 39,
  "fallecido": false
}
```

**Consume 1 crédito de Boostr.**

**Errores:**
- `404 Not Found`: Persona no encontrada
- `400 Bad Request`: RUT inválido

---

### 7.4. Consultar Vehículos de Persona

**GET** `/boostr/persona/{rut}/vehiculos`

Consulta los vehículos registrados a nombre de una persona.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
[
  {
    "patente": "ABCD12",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "tipo": "Automóvil"
  },
  {
    "patente": "EFGH34",
    "marca": "Honda",
    "modelo": "Civic",
    "año": 2018,
    "tipo": "Automóvil"
  }
]
```

**Consume 1 crédito de Boostr.**

---

### 7.5. Investigación Completa de Vehículo

**GET** `/boostr/investigar/vehiculo/{patente}`

**⚠️ IMPORTANTE: Este endpoint es GET, no POST**

Realiza una investigación completa de un vehículo.

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `oficio_id` (integer, optional): ID del oficio para registrar la actividad
- `incluir_multas` (boolean, default: true): Incluir consulta de multas

**Ejemplo de URL:**
```
GET /boostr/investigar/vehiculo/CFJV94?oficio_id=33&incluir_multas=true
```

**Response 200:**
```json
{
  "vehiculo": {
    "patente": "CFJV94",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "tipo": "Automóvil",
    "color": "Blanco",
    "vin": "JTD123456789",
    "combustible": "Gasolina",
    "kilometraje": 50000,
    "propietario_rut": "12345678-9",
    "propietario_nombre": "Pedro González"
  },
  "multas": [
    {
      "juzgado": "Juzgado de Policía Local de Santiago",
      "comuna": "Santiago",
      "rol": "12345-2023",
      "año": 2023,
      "fecha": "2023-05-15",
      "estado": "Pendiente",
      "monto": 50000.0
    }
  ],
  "creditos_usados": 2,
  "fecha_consulta": "2024-01-15T10:00:00Z"
}
```

**Consume 1-2 créditos de Boostr según las opciones.**

Si se proporciona `oficio_id`, registra la consulta en el timeline automáticamente.

---

### 7.6. Investigación Completa de Propietario

**GET** `/boostr/investigar/propietario/{rut}`

Realiza una investigación completa de un propietario.

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `oficio_id` (integer, optional): ID del oficio para registrar la actividad
- `incluir_vehiculos` (boolean, default: true): Incluir otros vehículos

**Ejemplo de URL:**
```
GET /boostr/investigar/propietario/12345678-9?oficio_id=33&incluir_vehiculos=true
```

**Response 200:**
```json
{
  "propietario": {
    "rut": "12345678-9",
    "nombre": "Pedro González Pérez",
    "nombres": "Pedro",
    "apellido_paterno": "González",
    "apellido_materno": "Pérez",
    "genero": "M",
    "nacionalidad": "Chilena",
    "fecha_nacimiento": "1985-03-15",
    "edad": 39,
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
  "fecha_consulta": "2024-01-15T10:00:00Z"
}
```

**Consume 1-2 créditos de Boostr según las opciones.**

---

### 7.7. Diagnóstico de Configuración (DEBUG)

**GET** `/boostr/debug/config`

**⚠️ ENDPOINT TEMPORAL - Solo para debugging. Debe ser removido en producción.**

Verifica la configuración de la API de Boostr.

**Headers:**
```
Authorization: Bearer {token}
```

**Requisito:** Solo usuarios con rol `admin` pueden acceder.

**Response 200:**
```json
{
  "boostr_url": "https://api.boostr.cl",
  "api_key_configured": true,
  "api_key_length": 42,
  "api_key_preview": "sk_live_ab...",
  "timeout": 30,
  "environment": "production",
  "user_rol": "admin"
}
```

**Uso:**
- Verificar que `api_key_configured` sea `true`
- Si es `false`, la variable `BOOSTR_API_KEY` no está configurada en Render.com
- Verificar que `api_key_length` > 0

---

## 8. Notificaciones

### 8.1. Obtener Notificaciones

**GET** `/notificaciones/oficios/{oficio_id}/notificaciones`

Obtiene el historial de notificaciones de un oficio.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "oficio_id": 1,
  "items": [
    {
      "id": 1,
      "oficio_id": 1,
      "tipo": "email",
      "destinatario": "cliente@example.com",
      "asunto": "Actualización de oficio",
      "contenido": "Se ha actualizado el estado del oficio",
      "enviada": true,
      "fecha_envio": "2024-01-15T10:00:00Z",
      "intentos": 1,
      "error_mensaje": null,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 8.2. Enviar Notificación

**POST** `/notificaciones/oficios/{oficio_id}/notificaciones`

Envía una notificación.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "tipo": "email",
  "destinatario": "cliente@example.com",
  "asunto": "Actualización de oficio",
  "contenido": "Se ha actualizado el estado del oficio"
}
```

**Response 201:** (mismo formato que GET items)

---

## 9. Documentos

### 9.1. Subida Masiva de Documentos

**POST** `/oficios/documents/upload-batch`

Sube múltiples documentos PDF (Oficio + CAV) para procesamiento automático.

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Form Data:**
- `files` (file[], required): Archivos PDF a procesar (máx. 200)
- `buffet_id` (integer, optional): ID del buffet asociado

**Response 202:**
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
      "storage_path": "/storage/abc123_oficio-001.pdf",
      "tipo_documento": "oficio",
      "status": "processing"
    },
    {
      "file_id": "def456",
      "file_name": "cav-001.pdf",
      "storage_path": "/storage/def456_cav-001.pdf",
      "tipo_documento": "cav",
      "status": "processing"
    }
  ],
  "buffet_id": 1,
  "status": "accepted",
  "message": "2 archivos subidos y en proceso"
}
```

**Tipos de documento detectados:**
- `oficio`: Oficio judicial
- `cav`: Certificado de Anotaciones Vigentes
- `desconocido`: No se pudo detectar

**Validaciones:**
- Máximo 200 archivos por batch
- Solo archivos PDF
- Tamaño máximo por archivo: según configuración

---

## Autenticación

Todos los endpoints (excepto `/auth/register`, `/auth/login`, `/auth/login/json`, `/health`, `/info`) requieren autenticación mediante JWT.

### Formato del Token

```
Authorization: Bearer {access_token}
```

### Obtener Token

1. Hacer login en `/auth/login` o `/auth/login/json`
2. Copiar el `access_token` de la respuesta
3. Incluir en el header `Authorization` de todas las requests

### Expiración

El token expira en 3600 segundos (1 hora). Después de expirar, debes hacer login nuevamente.

---

## Códigos de Error Comunes

| Código | Significado |
|--------|-------------|
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Conflicto de datos (ej: email duplicado) |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error del servidor |
| 502 | Bad Gateway - Error en servicio externo |

---

## Enumeraciones (Enums)

### Roles de Usuario
- `admin`: Administrador
- `investigador`: Investigador
- `cliente`: Cliente (buffet)

### Estados de Oficio
- `pendiente`: Pendiente de asignación
- `asignado`: Asignado a investigador
- `en_progreso`: En investigación
- `completado`: Investigación completada
- `archivado`: Oficio archivado

### Prioridad
- `baja`: Prioridad baja
- `media`: Prioridad media
- `alta`: Prioridad alta

### Tipo de Propietario
- `natural`: Persona natural
- `juridica`: Persona jurídica

### Tipo de Dirección
- `domicilio`: Domicilio principal
- `trabajo`: Lugar de trabajo
- `alternativa`: Dirección alternativa

### Resultado de Visita
- `exitosa`: Encontrado
- `no_encontrado`: No encontrado
- `direccion_incorrecta`: Dirección incorrecta
- `se_mudo`: Se mudó
- `rechazo_atencion`: Rechazó atención
- `otro`: Otro resultado

### Tipo de Actividad
- `llamada`: Llamada telefónica
- `visita`: Visita presencial
- `email`: Correo electrónico
- `consulta_api`: Consulta a API externa
- `otro`: Otra actividad

---

## Notas Importantes

1. **Paginación**: Los endpoints de listado soportan paginación mediante `skip` y `limit`
2. **Filtros**: Muchos endpoints soportan filtros opcionales
3. **Soft Delete**: Las eliminaciones son "soft delete" (se marca como inactivo, no se borra)
4. **Timestamps**: Todos los recursos tienen `created_at` y `updated_at`
5. **Validaciones**: El sistema valida RUT chileno, emails, etc.
6. **Créditos Boostr**: Las consultas a Boostr API consumen créditos
7. **Rate Limiting**: Boostr tiene rate limiting (máx. 60 requests/minuto)

---

## Cambios Recientes

- **2024-01-20**: Los endpoints `/boostr/investigar/vehiculo/{patente}` y `/boostr/investigar/propietario/{rut}` fueron cambiados de POST a **GET** con query parameters
- **2024-01-15**: Agregado endpoint de subida masiva de documentos
- **2024-01-10**: Agregados endpoints de visitas a direcciones

---

## Próximas Funcionalidades

- Webhooks de Google Drive para procesamiento automático
- Exportación de reportes en PDF
- Dashboard de métricas
- Notificaciones push
