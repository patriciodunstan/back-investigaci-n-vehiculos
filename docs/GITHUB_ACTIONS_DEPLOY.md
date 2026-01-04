# 🚀 Despliegue con GitHub Actions

Guía completa para configurar CI/CD con GitHub Actions y desplegar automáticamente.

## 📋 Ventajas de GitHub Actions

✅ **Control total sobre el entorno de build**
- Especifica Python 3.12 explícitamente
- Evita problemas de compatibilidad con Python 3.13

✅ **Builds reproducibles**
- Mismo entorno en desarrollo y producción
- Fácil debugging de problemas

✅ **Automatización completa**
- Tests automáticos antes de deploy
- Migraciones automáticas
- Notificaciones de estado

✅ **Flexibilidad**
- Puede desplegar a Render, Railway, Fly.io, o cualquier servicio
- Puede usar Docker para mayor portabilidad

---

## 🔧 Configuración Inicial

### Paso 1: Configurar Secrets en GitHub

Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions**

Agrega estos secrets:

1. **`DATABASE_URL`**
   ```
   postgresql://neondb_owner:npg_xxx@ep-xxx.neon.tech/investigaciones_db?sslmode=require
   ```

2. **`RENDER_API_KEY`** (opcional, si quieres trigger automático)
   - Obtén tu API key de: https://dashboard.render.com/account/api-keys

3. **`RENDER_SERVICE_ID`** (opcional)
   - ID de tu servicio en Render (se encuentra en la URL del servicio)

### Paso 2: Verificar Workflows

Los workflows ya están creados en:
- `.github/workflows/deploy.yml` - Build y deploy
- `.github/workflows/ci.yml` - Tests y linting

---

## 🎯 Opciones de Despliegue

### Opción 1: GitHub Actions → Render (Recomendado)

GitHub Actions hace el build y luego trigger un deploy en Render.

**Ventajas:**
- Build controlado (Python 3.12)
- Render maneja el hosting
- Fácil de configurar

**Configuración:**

1. El workflow `.github/workflows/deploy.yml` ya está configurado
2. Solo necesitas agregar los secrets de Render
3. Cada push a `main` triggerá un deploy automático

---

### Opción 2: GitHub Actions → Docker → Cualquier Servicio

Build una imagen Docker y despliégala donde quieras.

**Ventajas:**
- Máxima portabilidad
- Puedes usar Railway, Fly.io, AWS, etc.
- Build una vez, despliega en cualquier lugar

**Configuración:**

1. El `Dockerfile` ya está creado
2. Modifica `.github/workflows/deploy.yml` para:
   - Build la imagen Docker
   - Push a Docker Hub / GitHub Container Registry
   - Deploy a tu servicio preferido

---

### Opción 3: GitHub Actions → Build Local → Render Manual

GitHub Actions solo valida que el build funciona, luego despliegas manualmente.

**Ventajas:**
- Control total sobre cuándo desplegar
- Build validado antes de deploy manual

---

## 📝 Workflows Incluidos

### 1. `.github/workflows/deploy.yml`

**Qué hace:**
- ✅ Checkout del código
- ✅ Setup Python 3.12.7
- ✅ Instala dependencias
- ✅ Ejecuta migraciones (opcional)
- ✅ Ejecuta tests (opcional)
- ✅ Trigger deploy en Render (opcional)

**Cuándo se ejecuta:**
- Push a `main`
- Manualmente desde GitHub Actions

---

### 2. `.github/workflows/ci.yml`

**Qué hace:**
- ✅ Tests con PostgreSQL 17
- ✅ Linting (Ruff, Black, Pylint)
- ✅ Coverage reports

**Cuándo se ejecuta:**
- Pull requests
- Push a `main`

---

## 🔄 Flujo de Trabajo Recomendado

### Desarrollo Normal

```bash
# 1. Trabajas en una branch
git checkout -b feature/nueva-funcionalidad

# 2. Haces cambios y commits
git add .
git commit -m "Nueva funcionalidad"

# 3. Push a GitHub
git push origin feature/nueva-funcionalidad

# 4. Creas Pull Request
# → GitHub Actions ejecuta CI (tests, linting)

# 5. Merge a main
# → GitHub Actions ejecuta deploy automático
```

---

## 🐳 Usar Docker (Alternativa)

Si prefieres usar Docker directamente:

### Build Local

```bash
docker build -t investigaciones-backend:latest .
```

### Run Local

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="..." \
  investigaciones-backend:latest
```

### Deploy a Railway

1. Conecta tu repositorio en Railway
2. Railway detectará el `Dockerfile` automáticamente
3. Configura las variables de entorno
4. Deploy automático en cada push

### Deploy a Fly.io

```bash
# Instala flyctl
# https://fly.io/docs/getting-started/installing-flyctl/

# Login
fly auth login

# Launch app
fly launch

# Deploy
fly deploy
```

---

## ⚙️ Configurar Render con GitHub Actions

### Método 1: Trigger Manual Deploy

El workflow ya incluye un paso para trigger deploy en Render usando su API.

**Requisitos:**
- `RENDER_API_KEY` en GitHub Secrets
- `RENDER_SERVICE_ID` en GitHub Secrets

**Cómo obtener RENDER_SERVICE_ID:**
1. Ve a tu servicio en Render
2. La URL será: `https://dashboard.render.com/web/xxxxx-xxxx-xxxx`
3. El ID es la parte después de `/web/`

---

### Método 2: Render Auto-Deploy desde GitHub

1. En Render Dashboard → Tu Servicio → Settings
2. **Auto-Deploy**: Enabled
3. **Branch**: `main`
4. Render detectará los pushes automáticamente

**Nota:** Render seguirá usando Python 3.13 por defecto. Para forzar Python 3.12:
- Ve a Settings → Environment
- Selecciona Python 3.12.7 manualmente

---

## 🔍 Troubleshooting

### Error: "Python version not found"

**Solución:** Verifica que el workflow use `python-version: '3.12.7'`

### Error: "Dependencies installation failed"

**Solución:** 
- Verifica que `requirements.txt` no tenga dependencias incompatibles
- `asyncpg` está comentado (no se usa)
- `pandas` está comentado (no se usa)

### Error: "Render API key invalid"

**Solución:**
- Verifica que el API key sea correcto
- Asegúrate de que tenga permisos para el servicio

### Build funciona en GitHub Actions pero falla en Render

**Causa:** Render está usando Python 3.13

**Solución:**
1. Configura Python 3.12 manualmente en Render Dashboard
2. O usa Docker (Render puede usar Dockerfile)

---

## 📊 Monitoreo

### Ver Estado de Builds

1. Ve a tu repositorio en GitHub
2. Click en **Actions**
3. Verás el estado de todos los workflows

### Notificaciones

GitHub Actions puede enviar notificaciones a:
- Email
- Slack
- Discord
- Webhooks personalizados

---

## 🎉 Ventajas de Este Enfoque

✅ **Builds consistentes**: Siempre usa Python 3.12
✅ **Tests automáticos**: Valida antes de deploy
✅ **Rollback fácil**: Cada commit es rastreable
✅ **CI/CD completo**: Automatización end-to-end
✅ **Multi-plataforma**: Puede desplegar a cualquier servicio

---

## 📚 Recursos

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Render API Documentation](https://render.com/docs/api)
- [Docker Documentation](https://docs.docker.com/)
- [Railway Documentation](https://docs.railway.app/)
- [Fly.io Documentation](https://fly.io/docs/)

---

## 🔄 Próximos Pasos

1. ✅ Configurar secrets en GitHub
2. ✅ Hacer push de los cambios
3. ✅ Verificar que el workflow se ejecute
4. ✅ Configurar Python 3.12 en Render manualmente
5. ✅ Verificar que el deploy funcione

---

## 💡 Recomendación Final

**Para producción, recomiendo:**

1. **GitHub Actions** para CI/CD (builds, tests)
2. **Render con Python 3.12** configurado manualmente, O
3. **Railway/Fly.io con Docker** para máximo control

La combinación de GitHub Actions + Render es la más simple y efectiva.

