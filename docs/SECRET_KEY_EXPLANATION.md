# SECRET_KEY - Guía de Configuración

## 🔑 ¿Qué es SECRET_KEY?

La `SECRET_KEY` es una cadena secreta utilizada para:
- **Firmar tokens JWT** (autenticación)
- **Validar tokens** cuando los usuarios hacen requests

## 📋 Diferentes Contextos

### 1. **Tests / CI (GitHub Actions)**

**Valor actual:** `test-secret-key-for-ci-only-not-used-in-production`

**¿Es correcto?** ✅ **SÍ**

- Cualquier valor dummy está bien para tests
- Solo necesita que `Settings` pueda inicializarse
- **NO se usa para generar tokens reales**
- Los tests crean tokens de prueba que solo validan la lógica

**Valor recomendado:**
```yaml
SECRET_KEY: "test-secret-key-for-ci-only-not-used-in-production"
```

O para mantener consistencia con `tests/conftest.py`:
```yaml
SECRET_KEY: "test-secret-key-for-testing-only-min-32-chars"
```

Ambos son válidos para CI/tests.

---

### 2. **Desarrollo Local**

**Ubicación:** Archivo `.env` (en la raíz del proyecto)

**Valor recomendado:** Generar una clave única para tu entorno local

**Cómo generar:**
```bash
# Opción 1: Usar el script del proyecto
python scripts/generate_secret_key.py

# Opción 2: Usar Python directamente
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Opción 3: Usar OpenSSL
openssl rand -hex 32
```

**Ejemplo de `.env`:**
```env
SECRET_KEY=tu-clave-generada-aqui-minimo-32-caracteres
```

---

### 3. **Producción (Render, AWS, etc.)**

**Ubicación:** Variables de entorno del servidor/hosting

**IMPORTANTE:**
- ⚠️ **DEBE ser una clave única y segura**
- ⚠️ **NUNCA compartirla o subirla a Git**
- ⚠️ **Usar diferente clave para cada ambiente (staging, producción)**

**Cómo generar para producción:**
```bash
python scripts/generate_secret_key.py
```

Esto genera algo como:
```
atbARhC_hmIfPvF_RMsyASJA2nqHd4RWrNNYNrfUNkR9e8898H17ZT5psiR7z1a7
```

**Configurar en Render:**
1. Ve a tu servicio en Render Dashboard
2. Settings → Environment Variables
3. Agrega: `SECRET_KEY` = `[la-clave-generada]`
4. Guarda

---

## 🔒 Requisitos de Seguridad

### Longitud Mínima
- **Recomendado:** 64 caracteres (como genera el script)
- **Mínimo:** 32 caracteres (para JWT con HS256)

### Caracteres
- Debe ser aleatoria y criptográficamente segura
- El script usa `secrets.token_urlsafe(48)` que genera caracteres URL-safe

### Para Producción
- ✅ Usar `secrets.token_urlsafe(48)` o `openssl rand -hex 32`
- ❌ NO usar valores predecibles como "mi-clave-secreta-123"
- ❌ NO usar la misma clave en desarrollo y producción
- ❌ NO subir la clave a Git (está en `.gitignore`)

---

## 📝 Resumen

| Contexto | Valor | ¿Necesita ser segura? |
|----------|-------|----------------------|
| **Tests / CI** | `test-secret-key-for-ci-only-not-used-in-production` | ❌ No (cualquier valor dummy) |
| **Desarrollo Local** | Generar con script | ⚠️ Mejor sí (pero no crítica) |
| **Producción** | Generar con script | ✅ **SÍ, OBLIGATORIO** |

---

## ✅ Verificación

Para verificar que tu `SECRET_KEY` está configurada correctamente:

```python
from src.core.config import get_settings

settings = get_settings()
print(f"SECRET_KEY configurada: {len(settings.SECRET_KEY)} caracteres")
```

Si no está configurada, `Settings()` lanzará un error de validación.

---

## 🛠️ Script de Generación

El proyecto incluye un script para generar claves:

```bash
python scripts/generate_secret_key.py
```

Esto genera una clave segura de 64 caracteres usando `secrets.token_urlsafe(48)`.
