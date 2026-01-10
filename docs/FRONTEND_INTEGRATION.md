# API Frontend Integration Guide

Documentación de los nuevos endpoints implementados para integración con el frontend.

**Fecha:** 8 de enero de 2026  
**Versión API:** 1.1.0  
**Base URL:** `https://api.example.com/api/v1`

---

## ⚠️ BREAKING CHANGES v1.1.0

### Cambio en estructura de Oficios: `vehiculo` → `vehiculos`

**Antes (v1.0):**
```json
{
  "id": 1,
  "numero_oficio": "C-4695-2024",
  "vehiculo": {
    "id": 1,
    "patente": "ABCD12",
    "marca": "Toyota"
  }
}
```

**Ahora (v1.1):**
```json
{
  "id": 1,
  "numero_oficio": "C-4695-2024",
  "vehiculos": [
    {
      "id": 1,
      "patente": "JZRH618",
      "marca": "Nissan"
    },
    {
      "id": 2,
      "patente": "LGCR751",
      "marca": "Kia Motors"
    }
  ]
}
```

**Acciones requeridas en el frontend:**
1. Cambiar `oficio.vehiculo` por `oficio.vehiculos` (array)
2. Actualizar interfaces TypeScript
3. Renderizar lista de vehículos en lugar de uno solo

---

## 📋 Tabla de Contenidos

1. [Boostr API - Consultas Externas](#1-boostr-api---consultas-externas)
2. [Gestión de Direcciones y Visitas](#2-gestión-de-direcciones-y-visitas)
3. [Enums y Valores](#3-enums-y-valores)
4. [Ejemplos de Integración](#4-ejemplos-de-integración)

---

## 1. Boostr API - Consultas Externas

Endpoints para consultar información de vehículos y personas desde fuentes externas (Registro Civil, Registro de Vehículos, etc.).

> ⚠️ **Importante:** Cada consulta consume créditos de la API Boostr. Usar con moderación.

### 1.1 Consultar Vehículo por Patente

```http
GET /api/v1/investigaciones/boostr/vehiculo/{patente}
```

**Parámetros:**
| Param | Tipo | Ubicación | Descripción |
|-------|------|-----------|-------------|
| patente | string | path | Patente del vehículo (ej: "ABCD12") |

**Headers:**
```
Authorization: Bearer {token}
```

**Respuesta exitosa (200):**
```json
{
  "patente": "ABCD12",
  "marca": "TOYOTA",
  "modelo": "COROLLA",
  "año": 2020,
  "tipo": "AUTOMOVIL",
  "color": "BLANCO",
  "vin": "JTDBU4EE9A9123456",
  "combustible": "GASOLINA",
  "kilometraje": 45000,
  "propietario_rut": "12345678-9",
  "propietario_nombre": "JUAN PEREZ GONZALEZ"
}
```

**Errores posibles:**
| Código | Descripción |
|--------|-------------|
| 404 | Vehículo no encontrado |
| 429 | Rate limit excedido (esperar 1 minuto) |
| 502 | Error en servicio externo |

---

### 1.2 Consultar Multas de Vehículo

```http
GET /api/v1/investigaciones/boostr/vehiculo/{patente}/multas
```

**Respuesta exitosa (200):**
```json
[
  {
    "juzgado": "1er Juzgado de Policía Local de Santiago",
    "comuna": "Santiago",
    "rol": "12345-2024",
    "año": 2024,
    "fecha": "2024-03-15",
    "estado": "PENDIENTE",
    "monto": 45000.0
  }
]
```

> 💡 **Uso:** Las multas indican ubicaciones donde el vehículo ha sido visto.

---

### 1.3 Consultar Persona por RUT

```http
GET /api/v1/investigaciones/boostr/persona/{rut}
```

**Parámetros:**
| Param | Tipo | Ubicación | Descripción |
|-------|------|-----------|-------------|
| rut | string | path | RUT con dígito verificador (ej: "12345678-9") |

**Respuesta exitosa (200):**
```json
{
  "rut": "12345678-9",
  "nombre": "JUAN PEREZ GONZALEZ",
  "nombres": "JUAN ANTONIO",
  "apellido_paterno": "PEREZ",
  "apellido_materno": "GONZALEZ",
  "genero": "MASCULINO",
  "nacionalidad": "CHILE",
  "fecha_nacimiento": "1985-06-15",
  "edad": 40,
  "fallecido": false
}
```

**Errores posibles:**
| Código | Descripción |
|--------|-------------|
| 400 | RUT inválido |
| 404 | Persona no encontrada |
| 429 | Rate limit excedido |

---

### 1.4 Consultar Vehículos de una Persona

```http
GET /api/v1/investigaciones/boostr/persona/{rut}/vehiculos
```

**Respuesta exitosa (200):**
```json
[
  {
    "patente": "ABCD12",
    "marca": "TOYOTA",
    "modelo": "COROLLA",
    "año": 2020,
    "tipo": "AUTOMOVIL"
  },
  {
    "patente": "EFGH34",
    "marca": "SUZUKI",
    "modelo": "SWIFT",
    "año": 2018,
    "tipo": "AUTOMOVIL"
  }
]
```

---

### 1.5 Investigación Completa de Vehículo

```http
GET /api/v1/investigaciones/boostr/investigar/vehiculo/{patente}
```

**Query Params:**
| Param | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| oficio_id | int | null | ID del oficio para registrar actividad |
| incluir_multas | bool | true | Incluir multas en la respuesta |

**Respuesta exitosa (200):**
```json
{
  "vehiculo": {
    "patente": "ABCD12",
    "marca": "TOYOTA",
    "modelo": "COROLLA",
    "año": 2020,
    "tipo": "AUTOMOVIL",
    "color": "BLANCO",
    "vin": "JTDBU4EE9A9123456",
    "combustible": "GASOLINA",
    "kilometraje": 45000,
    "propietario_rut": "12345678-9",
    "propietario_nombre": "JUAN PEREZ GONZALEZ"
  },
  "multas": [
    {
      "juzgado": "1er Juzgado de Policía Local",
      "comuna": "Providencia",
      "rol": "5678-2024",
      "año": 2024,
      "fecha": "2024-05-20",
      "estado": "PAGADA",
      "monto": 30000.0
    }
  ],
  "creditos_usados": 2,
  "fecha_consulta": "2026-01-08T15:30:00Z"
}
```

---

### 1.6 Investigación Completa de Propietario

```http
GET /api/v1/investigaciones/boostr/investigar/propietario/{rut}
```

**Query Params:**
| Param | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| oficio_id | int | null | ID del oficio para registrar actividad |

**Respuesta exitosa (200):**
```json
{
  "propietario": {
    "rut": "12345678-9",
    "nombre": "JUAN PEREZ GONZALEZ",
    "nombres": "JUAN ANTONIO",
    "apellido_paterno": "PEREZ",
    "apellido_materno": "GONZALEZ",
    "genero": "MASCULINO",
    "nacionalidad": "CHILE",
    "fecha_nacimiento": "1985-06-15",
    "edad": 40,
    "fallecido": false
  },
  "vehiculos": [
    {
      "patente": "ABCD12",
      "marca": "TOYOTA",
      "modelo": "COROLLA",
      "año": 2020,
      "tipo": "AUTOMOVIL"
    }
  ],
  "creditos_usados": 2,
  "fecha_consulta": "2026-01-08T15:30:00Z"
}
```

---

## 2. Gestión de Direcciones y Visitas

Sistema para registrar visitas a direcciones durante la investigación y trackear el estado de verificación.

### 2.1 Registrar Visita a Dirección

```http
POST /api/v1/oficios/direcciones/{direccion_id}/visitas
```

**Parámetros:**
| Param | Tipo | Ubicación | Descripción |
|-------|------|-----------|-------------|
| direccion_id | int | path | ID de la dirección |

**Body (JSON):**
```json
{
  "resultado": "no_encontrado",
  "notas": "Se visitó a las 15:00, nadie respondió",
  "latitud": "-33.4489",
  "longitud": "-70.6693"
}
```

**Campos del body:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| resultado | enum | ✅ | Resultado de la visita (ver [Enums](#31-resultadoverificacionenum)) |
| notas | string | ❌ | Observaciones de la visita (max 2000 chars) |
| latitud | string | ❌ | Coordenada GPS |
| longitud | string | ❌ | Coordenada GPS |

**Respuesta exitosa (201):**
```json
{
  "id": 15,
  "direccion_id": 42,
  "investigador_id": 3,
  "investigador_nombre": "Carlos Investigador",
  "fecha_visita": "2026-01-08T15:30:00Z",
  "resultado": "no_encontrado",
  "notas": "Se visitó a las 15:00, nadie respondió",
  "latitud": "-33.4489",
  "longitud": "-70.6693"
}
```

**Errores posibles:**
| Código | Descripción |
|--------|-------------|
| 404 | Dirección no encontrada |
| 422 | Datos de validación inválidos |

---

### 2.2 Obtener Historial de Visitas

```http
GET /api/v1/oficios/direcciones/{direccion_id}/visitas
```

**Respuesta exitosa (200):**
```json
[
  {
    "id": 15,
    "direccion_id": 42,
    "investigador_id": 3,
    "investigador_nombre": "Carlos Investigador",
    "fecha_visita": "2026-01-08T15:30:00Z",
    "resultado": "no_encontrado",
    "notas": "Nadie respondió",
    "latitud": "-33.4489",
    "longitud": "-70.6693"
  },
  {
    "id": 12,
    "direccion_id": 42,
    "investigador_id": 3,
    "investigador_nombre": "Carlos Investigador",
    "fecha_visita": "2026-01-06T10:15:00Z",
    "resultado": "rechazo_atencion",
    "notas": "Vecino dijo que no conoce al propietario",
    "latitud": null,
    "longitud": null
  }
]
```

> 📝 Las visitas vienen ordenadas por fecha descendente (más reciente primero).

---

### 2.3 Obtener Direcciones Pendientes de un Oficio

```http
GET /api/v1/oficios/{oficio_id}/direcciones/pendientes
```

Retorna las direcciones que requieren verificación:
- Nunca visitadas (`pendiente`)
- Con resultado `no_encontrado` (reintentar)
- Con `rechazo_atencion` (reintentar)

**Respuesta exitosa (200):**
```json
[
  {
    "id": 42,
    "direccion": "Av. Providencia 1234, Depto 501",
    "comuna": "Providencia",
    "region": "Metropolitana",
    "tipo": "domicilio",
    "verificada": false,
    "resultado_verificacion": "pendiente",
    "fecha_verificacion": null,
    "verificada_por_id": null,
    "verificada_por_nombre": null,
    "cantidad_visitas": 0,
    "notas": null
  },
  {
    "id": 45,
    "direccion": "Los Leones 567",
    "comuna": "Providencia", 
    "region": "Metropolitana",
    "tipo": "trabajo",
    "verificada": false,
    "resultado_verificacion": "no_encontrado",
    "fecha_verificacion": "2026-01-06T10:15:00Z",
    "verificada_por_id": 3,
    "verificada_por_nombre": "Carlos Investigador",
    "cantidad_visitas": 2,
    "notas": "Parece oficina cerrada"
  }
]
```

---

### 2.4 Estructura de DireccionResponse Actualizada

Al obtener un oficio, las direcciones ahora incluyen campos adicionales:

```json
{
  "id": 42,
  "direccion": "Av. Providencia 1234, Depto 501",
  "comuna": "Providencia",
  "region": "Metropolitana",
  "tipo": "domicilio",
  "verificada": false,
  "resultado_verificacion": "pendiente",
  "fecha_verificacion": null,
  "verificada_por_id": null,
  "verificada_por_nombre": null,
  "cantidad_visitas": 0,
  "notas": null
}
```

**Nuevos campos:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| resultado_verificacion | enum | Estado actual de la verificación |
| verificada_por_id | int? | ID del último usuario que verificó |
| verificada_por_nombre | string? | Nombre del verificador |
| cantidad_visitas | int | Total de visitas realizadas |

---

## 3. Enums y Valores

### 3.1 ResultadoVerificacionEnum

Valores posibles para `resultado` al registrar una visita y para `resultado_verificacion` en direcciones:

| Valor | Descripción | UI Sugerida |
|-------|-------------|-------------|
| `pendiente` | No ha sido visitada | 🔵 Gris / Sin badge |
| `exitosa` | Se encontró al propietario/vehículo | ✅ Verde |
| `no_encontrado` | Nadie en el domicilio | ⚠️ Amarillo |
| `direccion_incorrecta` | La dirección no existe o es errónea | ❌ Rojo |
| `se_mudo` | El propietario ya no vive ahí | 🔄 Naranja |
| `rechazo_atencion` | Se negaron a atender | ⚠️ Amarillo |
| `otro` | Otro resultado | ⚪ Gris |

**Lógica de colores sugerida:**
```typescript
const getResultadoColor = (resultado: string) => {
  switch (resultado) {
    case 'exitosa': return 'green';
    case 'no_encontrado': 
    case 'rechazo_atencion': return 'yellow';
    case 'direccion_incorrecta': return 'red';
    case 'se_mudo': return 'orange';
    case 'pendiente':
    case 'otro':
    default: return 'gray';
  }
};
```

---

### 3.2 TipoDireccionEnum

```
domicilio   → Casa del propietario
trabajo     → Lugar de trabajo
familiar    → Casa de familiar
otro        → Otra dirección
```

---

## 4. Ejemplos de Integración

### 4.1 TypeScript - Tipos

```typescript
// types/boostr.ts
interface VehicleInfo {
  patente: string;
  marca: string | null;
  modelo: string | null;
  año: number | null;
  tipo: string | null;
  color: string | null;
  vin: string | null;
  combustible: string | null;
  kilometraje: number | null;
  propietario_rut: string | null;
  propietario_nombre: string | null;
}

interface PersonInfo {
  rut: string;
  nombre: string | null;
  nombres: string | null;
  apellido_paterno: string | null;
  apellido_materno: string | null;
  genero: string | null;
  nacionalidad: string | null;
  fecha_nacimiento: string | null;
  edad: number | null;
  fallecido: boolean | null;
}

interface TrafficFine {
  juzgado: string | null;
  comuna: string | null;
  rol: string | null;
  año: number | null;
  fecha: string | null;
  estado: string | null;
  monto: number | null;
}
```

```typescript
// types/direcciones.ts
type ResultadoVerificacion = 
  | 'pendiente'
  | 'exitosa'
  | 'no_encontrado'
  | 'direccion_incorrecta'
  | 'se_mudo'
  | 'rechazo_atencion'
  | 'otro';

interface Vehiculo {
  id: number;
  patente: string;
  marca: string | null;
  modelo: string | null;
  año: number | null;
  color: string | null;
  vin: string | null;
}

interface Propietario {
  id: number;
  rut: string;
  nombre_completo: string;
  email: string | null;
  telefono: string | null;
  tipo: 'principal' | 'codeudor' | 'aval' | 'usuario';
  direccion_principal: string | null;
  notas: string | null;
}

interface VisitaDireccion {
  id: number;
  direccion_id: number;
  investigador_id: number | null;
  investigador_nombre: string | null;
  fecha_visita: string;
  resultado: ResultadoVerificacion;
  notas: string | null;
  latitud: string | null;
  longitud: string | null;
}

interface Direccion {
  id: number;
  direccion: string;
  comuna: string | null;
  region: string | null;
  tipo: 'domicilio' | 'trabajo' | 'familiar' | 'otro';
  verificada: boolean;
  resultado_verificacion: ResultadoVerificacion;
  fecha_verificacion: string | null;
  verificada_por_id: number | null;
  verificada_por_nombre: string | null;
  cantidad_visitas: number;
  notas: string | null;
}

// ⚠️ ACTUALIZADO v1.1: vehiculos es ahora un array
interface Oficio {
  id: number;
  numero_oficio: string;
  buffet_id: number;
  buffet_nombre: string | null;
  investigador_id: number | null;
  investigador_nombre: string | null;
  estado: 'pendiente' | 'investigacion' | 'notificacion' | 'finalizado_encontrado' | 'finalizado_no_encontrado';
  prioridad: 'baja' | 'media' | 'alta' | 'urgente';
  fecha_ingreso: string;
  fecha_limite: string | null;
  notas_generales: string | null;
  vehiculos: Vehiculo[];  // ⚠️ ANTES: vehiculo: Vehiculo | null
  propietarios: Propietario[];
  direcciones: Direccion[];
  created_at: string;
  updated_at: string;
}

interface RegistrarVisitaRequest {
  resultado: ResultadoVerificacion;
  notas?: string;
  latitud?: string;
  longitud?: string;
}
```

---

### 4.2 React - Hook de Visitas

```typescript
// hooks/useVisitas.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useHistorialVisitas(direccionId: number) {
  return useQuery({
    queryKey: ['visitas', direccionId],
    queryFn: () => api.get(`/oficios/direcciones/${direccionId}/visitas`),
  });
}

export function useRegistrarVisita(direccionId: number) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: RegistrarVisitaRequest) => 
      api.post(`/oficios/direcciones/${direccionId}/visitas`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visitas', direccionId] });
      queryClient.invalidateQueries({ queryKey: ['oficios'] });
    },
  });
}

export function useDireccionesPendientes(oficioId: number) {
  return useQuery({
    queryKey: ['direcciones-pendientes', oficioId],
    queryFn: () => api.get(`/oficios/${oficioId}/direcciones/pendientes`),
  });
}
```

---

### 4.3 React - Componente de Registro de Visita

```tsx
// components/RegistrarVisitaModal.tsx
import { useState } from 'react';
import { useRegistrarVisita } from '@/hooks/useVisitas';

interface Props {
  direccionId: number;
  onClose: () => void;
}

const RESULTADOS = [
  { value: 'exitosa', label: 'Exitosa - Se encontró al propietario', icon: '✅' },
  { value: 'no_encontrado', label: 'No encontrado - Nadie en domicilio', icon: '⚠️' },
  { value: 'direccion_incorrecta', label: 'Dirección incorrecta', icon: '❌' },
  { value: 'se_mudo', label: 'Se mudó', icon: '🔄' },
  { value: 'rechazo_atencion', label: 'Rechazo de atención', icon: '🚫' },
  { value: 'otro', label: 'Otro', icon: '📝' },
];

export function RegistrarVisitaModal({ direccionId, onClose }: Props) {
  const [resultado, setResultado] = useState('');
  const [notas, setNotas] = useState('');
  
  const mutation = useRegistrarVisita(direccionId);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Obtener ubicación GPS si está disponible
    let coords = { latitud: undefined, longitud: undefined };
    if (navigator.geolocation) {
      try {
        const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject);
        });
        coords = {
          latitud: pos.coords.latitude.toString(),
          longitud: pos.coords.longitude.toString(),
        };
      } catch (e) {
        console.log('GPS no disponible');
      }
    }
    
    await mutation.mutateAsync({
      resultado: resultado as ResultadoVerificacion,
      notas: notas || undefined,
      ...coords,
    });
    
    onClose();
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Registrar Visita</h2>
      
      <div className="grid gap-2">
        {RESULTADOS.map((r) => (
          <label key={r.value} className="flex items-center gap-2">
            <input
              type="radio"
              name="resultado"
              value={r.value}
              checked={resultado === r.value}
              onChange={(e) => setResultado(e.target.value)}
            />
            <span>{r.icon}</span>
            <span>{r.label}</span>
          </label>
        ))}
      </div>
      
      <textarea
        placeholder="Notas adicionales..."
        value={notas}
        onChange={(e) => setNotas(e.target.value)}
        maxLength={2000}
      />
      
      <button type="submit" disabled={!resultado || mutation.isPending}>
        {mutation.isPending ? 'Guardando...' : 'Registrar Visita'}
      </button>
    </form>
  );
}
```

---

### 4.4 React - Badge de Estado

```tsx
// components/ResultadoBadge.tsx
interface Props {
  resultado: ResultadoVerificacion;
}

const CONFIG = {
  pendiente: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Pendiente' },
  exitosa: { bg: 'bg-green-100', text: 'text-green-700', label: 'Exitosa' },
  no_encontrado: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'No encontrado' },
  direccion_incorrecta: { bg: 'bg-red-100', text: 'text-red-700', label: 'Dirección incorrecta' },
  se_mudo: { bg: 'bg-orange-100', text: 'text-orange-700', label: 'Se mudó' },
  rechazo_atencion: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Rechazo' },
  otro: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Otro' },
};

export function ResultadoBadge({ resultado }: Props) {
  const config = CONFIG[resultado] || CONFIG.otro;
  
  return (
    <span className={`px-2 py-1 rounded-full text-sm ${config.bg} ${config.text}`}>
      {config.label}
    </span>
  );
}
```

---

### 4.5 React - Lista de Vehículos (NUEVO v1.1)

```tsx
// components/VehiculosList.tsx
import { Vehiculo, Oficio } from '@/types/direcciones';

interface Props {
  oficio: Oficio;
}

export function VehiculosList({ oficio }: Props) {
  const { vehiculos } = oficio;
  
  if (vehiculos.length === 0) {
    return <p className="text-gray-500">No hay vehículos registrados</p>;
  }
  
  return (
    <div className="space-y-3">
      <h3 className="font-semibold">
        Vehículos ({vehiculos.length})
      </h3>
      
      {vehiculos.map((vehiculo) => (
        <div 
          key={vehiculo.id} 
          className="p-3 border rounded-lg bg-white shadow-sm"
        >
          <div className="flex justify-between items-center">
            <span className="font-mono text-lg font-bold">
              {vehiculo.patente}
            </span>
            {vehiculo.color && (
              <span className="text-sm text-gray-500">
                {vehiculo.color}
              </span>
            )}
          </div>
          
          {(vehiculo.marca || vehiculo.modelo) && (
            <p className="text-sm text-gray-600 mt-1">
              {[vehiculo.marca, vehiculo.modelo, vehiculo.año]
                .filter(Boolean)
                .join(' ')}
            </p>
          )}
          
          {vehiculo.vin && (
            <p className="text-xs text-gray-400 mt-1 font-mono">
              VIN: {vehiculo.vin}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
```

**Ejemplo de migración de código existente:**

```tsx
// ❌ ANTES (v1.0) - vehiculo singular
function OficioDetail({ oficio }) {
  return (
    <div>
      <h2>{oficio.numero_oficio}</h2>
      {oficio.vehiculo ? (
        <p>Patente: {oficio.vehiculo.patente}</p>
      ) : (
        <p>Sin vehículo</p>
      )}
    </div>
  );
}

// ✅ AHORA (v1.1) - vehiculos array
function OficioDetail({ oficio }) {
  return (
    <div>
      <h2>{oficio.numero_oficio}</h2>
      {oficio.vehiculos.length > 0 ? (
        <ul>
          {oficio.vehiculos.map((v) => (
            <li key={v.id}>Patente: {v.patente}</li>
          ))}
        </ul>
      ) : (
        <p>Sin vehículos</p>
      )}
    </div>
  );
}
```

---

## 📌 Notas Importantes

1. **Autenticación:** Todos los endpoints requieren token JWT en header `Authorization: Bearer {token}`

2. **Rate Limiting Boostr:** Máximo 60 requests/minuto. Si se excede, se recibe error 429.

3. **Créditos Boostr:** Cada consulta consume créditos. Mostrar confirmación antes de consultas.

4. **GPS en Visitas:** Si el usuario permite ubicación, enviar coordenadas para trazabilidad.

5. **Direcciones Pendientes:** Incluye direcciones con `pendiente`, `no_encontrado` y `rechazo_atencion` para reintentos.

6. **⚠️ Vehículos v1.1:** Un oficio puede tener múltiples vehículos. Siempre iterar sobre `oficio.vehiculos[]` en lugar de acceder a `oficio.vehiculo` directamente.
