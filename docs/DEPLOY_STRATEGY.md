# 🎯 Estrategia de Despliegue

Guía para configurar el despliegue sin conflictos entre GitHub Actions y Render.

## 🔄 Situación Actual

Tienes **2 sistemas** que pueden hacer deploy automáticamente:

1. **GitHub Actions** (`.github/workflows/deploy.yml`)
2. **Render** (Auto-deploy desde GitHub)

Esto puede causar:
- ⚠️ Despliegues duplicados
- ⚠️ Conflictos de build
- ⚠️ Desperdicio de recursos

---

## ✅ Solución Recomendada: Validación + Deploy Único

### Estrategia: GitHub Actions valida, Render despliega

**Flujo:**
1. Push a `main` → GitHub Actions valida el build
2. Si la validación pasa → Render hace el deploy automático
3. Un solo deploy, sin conflictos

**Ventajas:**
- ✅ Build validado antes de deploy
- ✅ Un solo deploy (Render)
- ✅ Sin conflictos
- ✅ Feedback rápido si hay errores

---

## 🔧 Configuración Actual

### GitHub Actions (`.github/workflows/deploy.yml`)

**Ahora hace:**
- ✅ Valida que el build funciona
- ✅ Verifica dependencias
- ✅ NO hace deploy (solo validación)

**Cuándo se ejecuta:**
- Push a `main`
- Pull requests
- Manualmente

---

### Render

**Hace:**
- ✅ Deploy automático desde GitHub
- ✅ Build y deploy completo
- ✅ Ejecuta migraciones

**Configuración:**
- Auto-Deploy: Enabled
- Branch: `main`
- Python: 3.12.7 (configurar manualmente)

---

## 📋 Checklist de Configuración

### En Render Dashboard:

1. ✅ **Auto-Deploy habilitado**
   - Settings → Auto-Deploy: Enabled
   - Branch: `main`

2. ✅ **Python 3.12.7 configurado**
   - Settings → Environment
   - Python Version: 3.12.7

3. ✅ **Variables de entorno configuradas**
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `BACKEND_CORS_ORIGINS=["*"]`
   - Otras variables necesarias

---

## 🎯 Flujo de Trabajo

### Desarrollo Normal:

```bash
# 1. Trabajas en feature branch
git checkout -b feature/nueva-funcionalidad

# 2. Haces cambios
git add .
git commit -m "Nueva funcionalidad"

# 3. Push y creas PR
git push origin feature/nueva-funcionalidad
# → GitHub Actions ejecuta CI (tests, linting)

# 4. Merge a main
# → GitHub Actions valida build
# → Render detecta push y hace deploy automático
```

---

## 🔍 Verificar que Funciona

### 1. Ver GitHub Actions

1. Ve a tu repositorio → **Actions**
2. Deberías ver "Build Validation" ejecutándose
3. Debe pasar ✅ (verde)

### 2. Ver Render Deploy

1. Ve a Render Dashboard → Tu Servicio
2. Deberías ver un nuevo deploy iniciándose
3. Revisa los logs para ver el progreso

---

## ⚙️ Opciones Alternativas

### Opción A: Solo GitHub Actions (sin Render auto-deploy)

Si prefieres que GitHub Actions controle todo:

1. **Deshabilita Auto-Deploy en Render:**
   - Settings → Auto-Deploy: Disabled

2. **Configura secrets en GitHub:**
   - `RENDER_API_KEY`
   - `RENDER_SERVICE_ID`

3. **Habilita deploy en workflow:**
   - Descomenta el paso "Deploy to Render" en `.github/workflows/deploy.yml`

---

### Opción B: Solo Render (sin GitHub Actions)

Si prefieres que Render haga todo:

1. **Deshabilita el workflow de deploy:**
   - Renombra `.github/workflows/deploy.yml` a `.github/workflows/deploy.yml.disabled`

2. **Render hace todo:**
   - Build
   - Deploy
   - Migraciones

**Desventaja:** No hay validación previa del build

---

## 🎉 Configuración Actual (Recomendada)

**Estado:**
- ✅ GitHub Actions valida builds
- ✅ Render hace deploy automático
- ✅ Sin conflictos
- ✅ Validación antes de deploy

**Resultado:**
- Build validado → Deploy automático → Sin duplicados

---

## 📝 Notas Importantes

1. **Python 3.12 en Render:**
   - Debe configurarse manualmente en Render Dashboard
   - `runtime.txt` y `render.yaml` ayudan pero no garantizan

2. **Migraciones:**
   - Render ejecuta `alembic upgrade head` automáticamente
   - GitHub Actions solo valida, no ejecuta migraciones

3. **Tests:**
   - GitHub Actions ejecuta tests en PRs
   - Render no ejecuta tests (solo build y deploy)

---

## 🔄 Si Quieres Cambiar la Estrategia

### Para usar solo GitHub Actions:

1. Deshabilita Auto-Deploy en Render
2. Configura `RENDER_API_KEY` y `RENDER_SERVICE_ID` en GitHub Secrets
3. Modifica `.github/workflows/deploy.yml` para hacer deploy

### Para usar solo Render:

1. Renombra `.github/workflows/deploy.yml` a `.deploy.yml.disabled`
2. Render hará todo automáticamente

---

## ✅ Estado Actual

Tu configuración actual es **óptima**:
- GitHub Actions valida (sin deploy)
- Render despliega automáticamente
- Sin conflictos ni duplicados

¡Todo debería funcionar correctamente ahora! 🎉

