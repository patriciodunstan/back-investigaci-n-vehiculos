# 🐍 Configurar Python 3.12 en Render

## ⚠️ Problema CRÍTICO

Render está usando **Python 3.13.4 por defecto**, lo que causa múltiples problemas:

1. **SQLAlchemy**: Incompatibilidad con Python 3.13
2. **psycopg2-binary**: Error `undefined symbol: _PyInterpreterState_Get`

**Errores comunes:**
```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly but has additional attributes
ImportError: undefined symbol: _PyInterpreterState_Get
```

## ✅ Solución OBLIGATORIA

### ⚡ ACCIÓN REQUERIDA: Configurar Python 3.12 en el Dashboard

**Render NO respeta automáticamente `pythonVersion` en `render.yaml`**. Debes configurarlo manualmente:

#### Paso 1: Ir al Dashboard de Render

1. Ve a https://dashboard.render.com
2. Selecciona tu servicio `investigaciones-backend`

#### Paso 2: Configurar Python Version

1. Ve a **Settings** (configuración) en el menú lateral
2. Busca la sección **Environment** (Entorno)
3. Busca el campo **Python Version** o **Runtime**
4. **Cambia de "Python 3" o "Latest" a "Python 3.12.7"** (o la versión más reciente de 3.12 disponible)
5. **Guarda los cambios** (botón "Save Changes")

#### Paso 3: Limpiar Cache y Re-deploy

1. Ve a **Manual Deploy** en el menú superior
2. Selecciona **"Clear build cache & deploy"**
3. Espera a que termine el build

### Paso 4: Verificar que funciona

En los logs del build deberías ver:

```
🐍 Verificando versión de Python...
Python 3.12.7
✅ Python 3.12 detectado correctamente
```

**Si ves `Python 3.13.x` o el build falla con el mensaje de error, Render NO está usando Python 3.12.**

## 📋 Archivos de Configuración

Los siguientes archivos ya están configurados correctamente:

- ✅ `runtime.txt` → `python-3.12.7`
- ✅ `render.yaml` → `pythonVersion: 3.12.7`
- ✅ Build command verifica Python 3.12 y falla si no es correcto

**PERO estos archivos NO son suficientes. Debes configurar Python manualmente en el dashboard.**

## 🔍 Cómo Verificar la Versión de Python

### En los Logs del Build

Busca esta línea en los logs:
```
🐍 Verificando versión de Python...
Python 3.12.7  ← Debe decir 3.12.x, NO 3.13.x
```

### Si el Build Falla

Si ves este error en el build:
```
ERROR: Se requiere Python 3.12, pero se está usando 3.13.x
```

Significa que Render sigue usando Python 3.13. **Debes configurarlo manualmente en el dashboard.**

## 🚨 Si el Problema Persiste

### Opción 1: Recrear el Servicio desde Blueprint

1. Elimina el servicio actual
2. Crea un nuevo servicio desde el Blueprint (`render.yaml`)
3. Render debería respetar `pythonVersion: 3.12.7`

### Opción 2: Contactar Soporte de Render

Si ninguna de las opciones funciona, contacta al soporte de Render explicando que necesitas Python 3.12 pero el servicio está usando Python 3.13.

## 📝 Notas Importantes

- ⚠️ **Render usa Python 3.13 por defecto** desde finales de 2024
- ⚠️ **`render.yaml` no siempre se respeta** para la versión de Python
- ✅ **La configuración manual en el dashboard es la más confiable**
- ✅ **Python 3.12 es estable y compatible con todas las dependencias**

## 🔄 Después de Configurar Python 3.12

Una vez configurado correctamente:

1. ✅ El build debería completarse sin errores
2. ✅ Las migraciones se ejecutarán correctamente
3. ✅ La aplicación debería iniciar sin problemas
4. ✅ No deberías ver errores de `psycopg2` o `SQLAlchemy`

