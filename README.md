# Sistema de Investigaciones Vehiculares

API Backend para gestión de investigaciones de vehículos para estudios jurídicos.

## 📋 Descripción

Sistema backend desarrollado con **FastAPI** que permite gestionar investigaciones vehiculares, incluyendo:

- Autenticación JWT con roles (Admin, Investigador, Cliente)
- Gestión de buffets (estudios jurídicos clientes)
- Gestión de oficios de investigación
- Timeline de actividades de investigación
- Registro de avistamientos
- Sistema de notificaciones

## 🏗️ Arquitectura

El proyecto sigue los principios de **Clean Architecture** y está estructurado como **Modular Monolith**:

- **Clean Architecture**: Separación en capas (Domain, Application, Infrastructure, Presentation)
- **Modular Monolith**: Módulos independientes preparados para futura extracción a microservicios
- **SOLID Principles**: Código mantenible y extensible
- **DRY & KISS**: Evita duplicación y mantiene simplicidad

### Estructura del Proyecto

```
src/
├── core/                    # Configuración central
├── shared/                  # Componentes compartidos
│   ├── domain/             # Value Objects, Base Entity, Enums
│   ├── application/         # Interfaces, Event Bus
│   └── infrastructure/     # Database, Unit of Work
└── modules/                 # Módulos de negocio
    ├── usuarios/           # Autenticación y usuarios
    ├── buffets/            # Gestión de buffets
    ├── oficios/            # Gestión de oficios
    ├── investigaciones/    # Timeline y actividades
    └── notificaciones/     # Sistema de notificaciones
```

Cada módulo sigue la estructura:

```
module/
├── domain/          # Entidades, Value Objects, Excepciones
├── application/     # Use Cases, DTOs, Interfaces
├── infrastructure/  # Repositorios, Modelos SQLAlchemy, Servicios
└── presentation/   # Routers FastAPI, Schemas Pydantic
```

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI 0.109.0
- **Base de Datos**: PostgreSQL (SQLAlchemy 2.0)
- **Autenticación**: JWT (python-jose)
- **Validación**: Pydantic 2.5
- **Migraciones**: Alembic
- **Testing**: Pytest + pytest-cov
- **Linting**: Pylint, Ruff, Black
- **Async Tasks**: Celery + Redis
- **Email**: aiosmtplib

## 📦 Requisitos Previos

- Python 3.11+
- PostgreSQL 17+ (recomendado) o 15+
- Redis (para Celery)
- Docker y Docker Compose (opcional)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd back-investigación-vehiculos
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Editar `.env` con tus valores:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/investigaciones_db
SECRET_KEY=tu-clave-secreta-de-al-menos-32-caracteres
REDIS_URL=redis://localhost:6379/0
```

### 5. Iniciar servicios con Docker Compose

```bash
docker-compose up -d
```

Esto iniciará:
- PostgreSQL en puerto 5432
- Redis en puerto 6379

### 6. Ejecutar migraciones

```bash
alembic upgrade head
```

### 7. Crear usuario admin inicial

```bash
python scripts/seed_admin.py
```

Credenciales por defecto:
- Email: `admin@sistema.com`
- Password: `admin123`

## ▶️ Ejecución

### Desarrollo

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

O usando el script:

```bash
python src/main.py
```

La API estará disponible en:
- **API**: http://127.0.0.1:8000
- **Documentación Swagger**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Producción

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🧪 Testing

### Ejecutar todos los tests

```bash
# Windows
.\scripts\run_tests.ps1

# Linux/Mac
./scripts/run_tests.sh
```

### Solo tests unitarios

```bash
# Windows
.\scripts\run_tests_unit.ps1

# Linux/Mac
./scripts/run_tests_unit.sh
```

### Solo tests de integración

```bash
# Windows
.\scripts\run_tests_integration.ps1

# Linux/Mac
./scripts/run_tests_integration.sh
```

### Generar reporte de coverage

```bash
# Windows
.\scripts\coverage_report.ps1

# Linux/Mac
./scripts/coverage_report.sh
```

El reporte HTML estará en `htmlcov/index.html`.

## 📚 Endpoints Principales

### Autenticación

- `POST /api/v1/auth/register` - Registrar nuevo usuario
- `POST /api/v1/auth/login` - Login (form-data o JSON)
- `GET /api/v1/auth/me` - Obtener usuario actual

### Buffets

- `GET /api/v1/buffets` - Listar buffets
- `POST /api/v1/buffets` - Crear buffet
- `GET /api/v1/buffets/{id}` - Obtener buffet
- `PUT /api/v1/buffets/{id}` - Actualizar buffet
- `DELETE /api/v1/buffets/{id}` - Eliminar buffet

### Oficios

- `GET /api/v1/oficios` - Listar oficios
- `POST /api/v1/oficios` - Crear oficio
- `GET /api/v1/oficios/{id}` - Obtener oficio
- `PUT /api/v1/oficios/{id}` - Actualizar oficio
- `POST /api/v1/oficios/{id}/propietarios` - Agregar propietario
- `POST /api/v1/oficios/{id}/direcciones` - Agregar dirección

### Investigaciones

- `POST /api/v1/investigaciones/oficios/{id}/actividades` - Agregar actividad
- `POST /api/v1/investigaciones/oficios/{id}/avistamientos` - Agregar avistamiento
- `GET /api/v1/investigaciones/oficios/{id}/timeline` - Obtener timeline

### Notificaciones

- `POST /api/v1/notificaciones/oficios/{id}/notificaciones` - Crear notificación
- `GET /api/v1/notificaciones/oficios/{id}/notificaciones` - Listar notificaciones

Ver documentación completa en `/docs` cuando el servidor esté corriendo.

## 🔐 Autenticación

La API usa JWT Bearer tokens. Para usar endpoints protegidos:

```bash
# Login
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@sistema.com&password=admin123"

# Usar token en requests
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <token>"
```

## 📖 Documentación Adicional

- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Guía para desarrolladores
- [API.md](docs/API.md) - Documentación detallada de API
- [TESTING.md](docs/TESTING.md) - Guía de testing
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Guía de despliegue

## 🤝 Contribución

1. Crear branch desde `main`
2. Realizar cambios
3. Ejecutar tests y verificar coverage
4. Crear Pull Request

## 📝 Licencia

[Especificar licencia]

## 👥 Autores

[Especificar autores]

