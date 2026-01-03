# Configuración de Neon PostgreSQL

Guía paso a paso para configurar Neon y conectar el backend.

## 🚀 Paso 1: Crear Base de Datos en Neon

1. Ve a [Neon Console](https://console.neon.tech/)
2. Inicia sesión o crea una cuenta
3. Crea un nuevo proyecto:
   - Nombre: `investigaciones-vehiculares` (o el que prefieras)
   - Región: Elige la más cercana (ej: `us-east-1`)
   - PostgreSQL: **Versión 17** (recomendado) o superior

## 🔑 Paso 2: Obtener Connection String

1. En el dashboard de Neon, ve a la sección **Connection Details**
2. Copia la **Connection String** (formato `postgresql://...`)
3. Ejemplo:
   ```
   postgresql://user:password@ep-xxx-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

## ⚙️ Paso 3: Configurar Variables de Entorno

### Opción A: Archivo `.env` (Desarrollo Local)

Crea o edita `.env` en la raíz del proyecto:

```env
# Environment
ENVIRONMENT=production
DEBUG=false

# Database - Reemplaza con tu Connection String de Neon
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Security - Genera una clave secreta fuerte
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-de-al-menos-32-caracteres-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (opcional para desarrollo local)
REDIS_URL=redis://localhost:6379/0

# CORS - Agrega tu dominio de producción
BACKEND_CORS_ORIGINS=["https://tu-dominio.com","https://www.tu-dominio.com"]

# Logging
LOG_LEVEL=INFO
```

### Opción B: Variables de Entorno del Sistema (Producción)

En Render, configura estas variables en el dashboard.

## ✅ Paso 4: Verificar Conexión

Ejecuta el script de verificación:

```bash
python scripts/setup_neon.py
```

Este script:
- ✅ Verifica la conexión a Neon
- ✅ Muestra la versión de PostgreSQL
- ✅ Lista las tablas existentes

## 📊 Paso 5: Ejecutar Migraciones

Una vez verificada la conexión, ejecuta las migraciones:

```bash
alembic upgrade head
```

Esto creará todas las tablas necesarias en Neon.

## 👤 Paso 6: Crear Usuario Admin

Ejecuta el script para crear el usuario admin inicial:

```bash
python scripts/seed_admin.py
```

Credenciales por defecto:
- Email: `admin@sistema.com`
- Password: `admin123`

**⚠️ IMPORTANTE**: Cambia estas credenciales en producción.

## 🔍 Verificar que Todo Funciona

Ejecuta el servidor localmente para probar:

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Prueba el endpoint de health:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## 🐛 Troubleshooting

### Error: "connection refused"

- Verifica que el proyecto Neon esté activo
- Verifica que la Connection String sea correcta
- Verifica que `sslmode=require` esté en la URL

### Error: "authentication failed"

- Verifica el usuario y contraseña en la Connection String
- Regenera la contraseña en Neon si es necesario

### Error: "database does not exist"

- Verifica el nombre de la base de datos en la Connection String
- Neon crea una base de datos por defecto llamada `neondb`

### Error: "relation does not exist"

- Ejecuta las migraciones: `alembic upgrade head`

## 📝 Notas Importantes

1. **SSL Required**: Neon requiere SSL. Asegúrate de que `sslmode=require` esté en la URL.

2. **Connection Pooling**: Neon tiene límites de conexiones. El código ya está configurado con pool de conexiones.

3. **Backups**: Neon hace backups automáticos. No necesitas configurar nada adicional.

4. **Escalado**: Neon escala automáticamente según el uso.

## 🔗 Recursos

- [Neon Documentation](https://neon.tech/docs)
- [Neon Connection Strings](https://neon.tech/docs/connect/connect-from-any-app)
- [PostgreSQL SSL Connection](https://neon.tech/docs/connect/connect-securely)

