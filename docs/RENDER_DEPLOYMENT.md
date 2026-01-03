# Despliegue en Render

Guía completa para desplegar el backend en Render con Neon PostgreSQL.

## 📋 Prerequisitos

1. ✅ Cuenta en [Render](https://render.com/)
2. ✅ Base de datos Neon configurada (ver [NEON_SETUP.md](NEON_SETUP.md))
3. ✅ Código en un repositorio Git (GitHub, GitLab, etc.)

## 🚀 Paso 1: Preparar el Repositorio

Asegúrate de que tu código esté en un repositorio Git y que esté actualizado:

```bash
git add .
git commit -m "Preparar para despliegue en Render"
git push origin main
```

## 🔧 Paso 2: Crear Web Service en Render

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. Click en **New +** → **Web Service**
3. Conecta tu repositorio:
   - Selecciona el repositorio donde está el código
   - Branch: `main` (o la rama que uses)

## ⚙️ Paso 3: Configurar el Servicio

### Configuración Básica

- **Name**: `investigaciones-backend` (o el nombre que prefieras)
- **Environment**: `Python 3`
- **Region**: Elige la región más cercana
- **Branch**: `main`
- **Root Directory**: (dejar vacío si el código está en la raíz)

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

**Nota**: Render proporciona la variable `$PORT` automáticamente.

## 🔐 Paso 4: Configurar Variables de Entorno

En la sección **Environment Variables** de Render, agrega:

### Variables Requeridas

```env
ENVIRONMENT=production
DEBUG=false
APP_NAME=Sistema de Investigaciones Vehiculares
API_V1_STR=/api/v1

# Database - Tu Connection String de Neon
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Security - Genera una clave secreta fuerte
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-de-al-menos-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Agrega tu dominio frontend
BACKEND_CORS_ORIGINS=["https://tu-dominio.com","https://www.tu-dominio.com"]

# Logging
LOG_LEVEL=INFO
```

### Variables Opcionales

```env
# Redis (si usas Redis en Render)
REDIS_URL=redis://red-xxx:6379

# Email (si configuras SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM=noreply@tu-dominio.com

# Storage
STORAGE_TYPE=local
STORAGE_PATH=/opt/render/project/src/storage
```

## 📊 Paso 5: Ejecutar Migraciones en Build

Para ejecutar migraciones automáticamente al desplegar, puedes modificar el **Build Command**:

```bash
pip install -r requirements.txt && alembic upgrade head
```

O crear un script `render-build.sh`:

```bash
#!/bin/bash
set -e

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Ejecutando migraciones..."
alembic upgrade head

echo "Build completado"
```

Y usar como Build Command:

```bash
chmod +x render-build.sh && ./render-build.sh
```

## 🚀 Paso 6: Desplegar

1. Click en **Create Web Service**
2. Render comenzará a construir y desplegar tu aplicación
3. Espera a que termine el build (puede tardar varios minutos la primera vez)

## ✅ Paso 7: Verificar Despliegue

Una vez desplegado, Render te dará una URL como:
```
https://investigaciones-backend.onrender.com
```

Prueba los endpoints:

```bash
# Health check
curl https://tu-app.onrender.com/api/v1/health

# Info
curl https://tu-app.onrender.com/api/v1/info
```

## 🔄 Paso 8: Configurar Auto-Deploy

Render despliega automáticamente cuando haces push a la rama configurada.

Para desactivar auto-deploy:
- Ve a **Settings** → **Auto-Deploy** → Desactiva

## 📝 Paso 9: Crear Usuario Admin

Una vez desplegado, ejecuta el script de seed localmente apuntando a Neon:

```bash
# Configurar DATABASE_URL en .env local apuntando a Neon
export DATABASE_URL="postgresql://..."
python scripts/seed_admin.py
```

O crea un script de one-time job en Render.

## 🔍 Monitoreo y Logs

### Ver Logs

En Render Dashboard:
- Ve a tu servicio → **Logs**
- Los logs se actualizan en tiempo real

### Health Checks

Render verifica automáticamente el endpoint `/api/v1/health`.

## 🐛 Troubleshooting

### Build Falla

1. Verifica los logs de build en Render
2. Asegúrate de que `requirements.txt` tenga todas las dependencias
3. Verifica que Python 3.11+ esté disponible

### La App No Inicia

1. Verifica los logs en tiempo real
2. Verifica que `DATABASE_URL` esté configurada correctamente
3. Verifica que el `Start Command` sea correcto

### Error de Conexión a Base de Datos

1. Verifica que `DATABASE_URL` tenga `sslmode=require`
2. Verifica que Neon permita conexiones desde Render (debería por defecto)
3. Verifica que las credenciales sean correctas

### Migraciones No Se Ejecutan

1. Ejecuta manualmente desde Render Shell:
   - Ve a **Shell** en Render Dashboard
   - Ejecuta: `alembic upgrade head`

## 💰 Planes de Render

- **Free Tier**: 
  - ✅ Suficiente para desarrollo/testing
  - ⚠️ El servicio se "duerme" después de 15 min de inactividad
  - ⚠️ Primera petición después de dormir puede tardar ~30 segundos

- **Starter Plan ($7/mes)**:
  - ✅ Sin sleep
  - ✅ Mejor rendimiento
  - ✅ Recomendado para producción

## 🔒 Seguridad

### Variables Sensibles

- ✅ Nunca commits `SECRET_KEY` o passwords al repositorio
- ✅ Usa siempre variables de entorno en Render
- ✅ Rota `SECRET_KEY` periódicamente

### HTTPS

Render proporciona HTTPS automáticamente con certificado SSL.

### CORS

Configura `BACKEND_CORS_ORIGINS` solo con dominios permitidos:

```env
BACKEND_CORS_ORIGINS=["https://tu-dominio.com"]
```

## 📚 Recursos Adicionales

- [Render Documentation](https://render.com/docs)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render Python Guide](https://render.com/docs/deploy-python)

## 🎯 Checklist de Despliegue

- [ ] Repositorio Git configurado
- [ ] Base de datos Neon creada y configurada
- [ ] Variables de entorno configuradas en Render
- [ ] Build Command configurado
- [ ] Start Command configurado
- [ ] Migraciones ejecutadas
- [ ] Usuario admin creado
- [ ] Health check funcionando
- [ ] CORS configurado correctamente
- [ ] Logs verificados

