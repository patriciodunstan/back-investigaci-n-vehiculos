# 🐍 Configurar Python 3.12 en Render

## ⚠️ Problema

Render está usando Python 3.13.4 por defecto, lo que causa incompatibilidad con SQLAlchemy 2.0.25.

**Error:**
```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly but has additional attributes
```

## ✅ Solución

### Paso 1: Configurar Python 3.12 en el Dashboard de Render

1. Ve a tu servicio en Render Dashboard
2. Ve a **Settings** → **Environment**
3. Busca **Python Version**
4. Selecciona **Python 3.12.7** (o la versión más reciente de 3.12 disponible)
5. Guarda los cambios

### Paso 2: Verificar archivos de configuración

Los siguientes archivos ya están configurados correctamente:

- ✅ `runtime.txt` → `python-3.12.7`
- ✅ `render.yaml` → `pythonVersion: 3.12.7`

### Paso 3: Forzar rebuild

Después de cambiar la versión de Python en el dashboard:

1. Ve a **Manual Deploy** → **Clear build cache & deploy**
2. O simplemente haz un nuevo push a `main`

## 🔍 Verificar que funciona

En los logs del build deberías ver:

```
🐍 Verificando versión de Python...
Python 3.12.7
```

Si ves `Python 3.13.x`, Render no está respetando la configuración.

## 📝 Notas

- El `render.yaml` especifica `pythonVersion: 3.12.7`, pero Render a veces lo ignora
- La configuración manual en el dashboard es más confiable
- SQLAlchemy 2.0.36+ tiene mejor compatibilidad con Python 3.13, pero aún se recomienda Python 3.12

## 🔄 Si el problema persiste

1. Verifica que el servicio esté usando el Blueprint (`render.yaml`)
2. Si no, crea el servicio desde el Blueprint
3. O configura Python manualmente en Settings → Environment

