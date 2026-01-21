# Diagnóstico del Problema con Boostr API

## 🔴 Problema Actual

Al hacer requests a `/boostr/investigar/vehiculo/CFJV94`:

```
Status: 502 Bad Gateway
Error: "Boostr API devolvió respuesta inválida (status: 403, Content-Type: text/html; charset=UTF-8)"
```

La API de Boostr está bloqueando las requests con un **403 Forbidden** y retornando HTML (página de error de Cloudflare) en lugar de JSON.

## 📋 Causas Posibles

### 1. ❌ API Key No Configurada o Incorrecta

**Síntoma:** El error 403 HTML indica que Cloudflare/WAF está bloqueando la request.

**Verificación:**
1. Revisar los logs del servidor al iniciar (buscar en Render.com logs):
   ```
   BoostrClient inicializado: base_url=..., api_key=***XXXX, timeout=30s
   ```

2. Si dice `api_key=NO CONFIGURADA`, la variable de entorno no está configurada.

**Solución:**
1. Ir a Render.com → Tu servicio → Environment
2. Verificar que exista la variable: `BOOSTR_API_KEY=tu_api_key_aqui`
3. Si no existe o está mal, agregarla/corregirla
4. Hacer redeploy del servicio

---

### 2. ⚠️ IP de Render.com Bloqueada

Boostr puede estar bloqueando las IPs de Render.com por:
- Demasiadas requests desde esa IP
- Detección como bot/scraper
- Lista negra de IPs de hosting

**Solución:**
- Contactar soporte de Boostr para whitelist de la IP
- Usar proxy si es necesario

---

### 3. 🚫 Header `x-api-key` Incorrecto

Algunas APIs usan:
- `x-api-key` ✅ (actual)
- `X-API-Key` (capitalizado)
- `Authorization: Bearer {key}`
- `api-key`

**Verificación:**
Revisar documentación de Boostr: https://docs.boostr.cl/reference

---

### 4. 🤖 Falta User-Agent Válido

**Ya corregido** en el código:
```python
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
```

Cloudflare bloquea requests sin User-Agent o con User-Agents sospechosos.

---

## 🔧 Pasos para Diagnosticar

### Paso 1: Verificar Variables de Entorno en Render.com

1. Ir a: https://dashboard.render.com
2. Seleccionar el servicio `investigaciones-backend`
3. Ir a **Environment** (menú izquierdo)
4. Verificar que existan:
   ```
   BOOSTR_API_KEY=sk_live_xxxxxxxxxxxx
   BOOSTR_API_URL=https://api.boostr.cl
   ```

### Paso 2: Verificar Logs del Servidor

1. Ir a **Logs** en Render.com
2. Buscar al inicio del deploy:
   ```
   BoostrClient inicializado: base_url=https://api.boostr.cl, api_key=***XXXX
   ```
3. Si dice `api_key=NO CONFIGURADA`, el problema está aquí.

### Paso 3: Verificar Request Real con Logging

Buscar en logs cuando se hace una request:
```
Boostr request: GET https://api.boostr.cl/vehicle/CFJV94.json
```

Y luego:
```
❌ Intentando hacer request sin API key
```

Si aparece este mensaje, la API key no está llegando.

### Paso 4: Test Directo con curl

Desde tu terminal local, probar la API de Boostr directamente:

```bash
curl -X GET "https://api.boostr.cl/vehicle/CFJV94.json" \
  -H "x-api-key: TU_API_KEY_AQUI" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

**Resultados esperados:**

✅ **Si funciona (200 OK):**
```json
{
  "status": "success",
  "data": {
    "brand": "Toyota",
    ...
  }
}
```

❌ **Si falla con 401:**
```json
{
  "status": "error",
  "message": "API Key inválida"
}
```
→ La API key está mal o no tiene créditos

❌ **Si falla con 403 HTML:**
```html
<!DOCTYPE html>
<html>...Cloudflare...</html>
```
→ Tu IP está bloqueada o falta algo en headers

---

## ✅ Soluciones por Orden de Probabilidad

### Solución 1: Configurar API Key en Render.com

**Más probable**

1. Ir a Render.com → Environment
2. Agregar/corregir:
   ```
   BOOSTR_API_KEY=sk_live_xxxxxxxxxxxx
   ```
3. Click en **Save Changes**
4. Redeploy automático se activará
5. Esperar 2-3 minutos y probar nuevamente

### Solución 2: Verificar Formato de API Key

Algunas APIs requieren prefijo:
- `Bearer {key}`
- `sk_live_{key}`
- Solo el key sin prefijo

Verificar en documentación de Boostr.

### Solución 3: Cambiar Header de API Key

Si Boostr usa otro header, editar `client.py`:

```python
# Probar con:
headers["Authorization"] = f"Bearer {self.api_key}"
# O:
headers["X-API-Key"] = self.api_key
# O:
headers["api-key"] = self.api_key
```

### Solución 4: Contactar Soporte de Boostr

Si nada funciona:
1. Verificar que tu cuenta de Boostr tenga créditos
2. Verificar que tu plan permita acceso a API
3. Contactar soporte para whitelist de IP de Render.com

---

## 📝 Endpoint de Diagnóstico (Opcional)

Puedes agregar un endpoint temporal para diagnóstico:

```python
# En boostr_router.py
@router.get("/debug/config")
async def debug_boostr_config(
    current_user: UserResponse = Depends(get_current_user)
):
    """Endpoint de diagnóstico - REMOVER EN PRODUCCIÓN"""
    settings = get_settings()
    return {
        "boostr_url": settings.BOOSTR_API_URL,
        "api_key_configured": bool(settings.BOOSTR_API_KEY),
        "api_key_length": len(settings.BOOSTR_API_KEY) if settings.BOOSTR_API_KEY else 0,
        "api_key_preview": settings.BOOSTR_API_KEY[:10] + "..." if settings.BOOSTR_API_KEY else "NO CONFIGURADA",
        "timeout": settings.BOOSTR_TIMEOUT,
    }
```

**⚠️ IMPORTANTE:** Este endpoint expone información sensible. Solo usar para debugging y remover después.

---

## 🎯 Acción Inmediata Recomendada

1. **Verificar en Render.com** que `BOOSTR_API_KEY` existe
2. **Revisar logs** al inicio del deploy para ver si la API key se carga
3. **Hacer deploy** si faltaba la variable
4. **Probar nuevamente** el endpoint

Si después de esto sigue fallando, el problema es con Boostr (IP bloqueada, créditos, etc.)

---

## 📚 Recursos

- **Documentación Boostr:** https://docs.boostr.cl/reference
- **Render.com Environment Variables:** https://render.com/docs/environment-variables
- **Logs en Render:** Dashboard → Tu servicio → Logs
