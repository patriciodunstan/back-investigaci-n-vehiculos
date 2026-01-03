# Guía de Despliegue

Esta guía explica cómo desplegar la aplicación en producción.

## 🐳 Docker

### Docker Compose

El proyecto incluye `docker-compose.yml` para desarrollo. Para producción, crear `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: investigaciones_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@db:5432/investigaciones_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
      DEBUG: false
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Ejecutar migraciones y servidor
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔐 Variables de Entorno

### Producción

Crear `.env.production`:

```env
# Environment
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/investigaciones_db

# Security
SECRET_KEY=clave-secreta-muy-larga-y-segura-de-al-menos-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://redis-host:6379/0

# CORS
BACKEND_CORS_ORIGINS=["https://tu-dominio.com"]

# Email (si aplica)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-password
SMTP_FROM=noreply@tu-dominio.com

# Logging
LOG_LEVEL=INFO
```

### Seguridad

- **SECRET_KEY**: Generar con `openssl rand -hex 32`
- **DB_PASSWORD**: Usar contraseña fuerte
- **CORS**: Configurar solo dominios permitidos
- **DEBUG**: Siempre `false` en producción

## 🚀 Despliegue

### 1. Preparar Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose
```

### 2. Clonar Repositorio

```bash
git clone <repository-url>
cd back-investigación-vehiculos
```

### 3. Configurar Variables

```bash
cp .env.example .env.production
# Editar .env.production con valores de producción
```

### 4. Construir y Ejecutar

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 5. Ejecutar Migraciones

```bash
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head
```

### 6. Verificar

```bash
curl http://localhost:8000/api/v1/health
```

## 🔄 Actualización

### 1. Pull Cambios

```bash
git pull origin main
```

### 2. Reconstruir

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Migraciones

```bash
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head
```

## 📊 Monitoreo

### Logs

```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs -f app

# Últimas 100 líneas
docker-compose -f docker-compose.prod.yml logs --tail=100 app
```

### Health Check

Endpoint `/api/v1/health` retorna estado del sistema.

### Métricas

Considerar integrar:
- Prometheus para métricas
- Grafana para visualización
- Sentry para errores

## 🔒 Seguridad

### Checklist

- [ ] `DEBUG=false` en producción
- [ ] `SECRET_KEY` fuerte y único
- [ ] CORS configurado correctamente
- [ ] Base de datos con contraseña fuerte
- [ ] HTTPS habilitado (usar nginx como reverse proxy)
- [ ] Rate limiting configurado
- [ ] Logs no contienen información sensible
- [ ] Backups de base de datos programados

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.tu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL con Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.tu-dominio.com
```

## 💾 Backups

### Base de Datos

```bash
# Backup manual
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres investigaciones_db > backup_$(date +%Y%m%d).sql

# Restaurar
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres investigaciones_db < backup_20240115.sql
```

### Automatizar Backups

Crear script `scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres investigaciones_db > $BACKUP_DIR/backup_$DATE.sql
# Eliminar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

Agregar a crontab:

```bash
0 2 * * * /path/to/scripts/backup.sh
```

## 🔧 Troubleshooting

### La aplicación no inicia

1. Verificar logs: `docker-compose logs app`
2. Verificar variables de entorno
3. Verificar conexión a base de datos

### Migraciones fallan

```bash
# Ver estado de migraciones
docker-compose exec app alembic current

# Revertir última migración
docker-compose exec app alembic downgrade -1
```

### Performance

- Aumentar workers: `--workers 4`
- Configurar pool de conexiones en SQLAlchemy
- Usar Redis para cache (futuro)
- Monitorear queries lentas

## 📚 Recursos

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL Backup](https://www.postgresql.org/docs/current/backup.html)

