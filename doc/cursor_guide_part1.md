# Guía Completa de Implementación - Sistema de Investigaciones Vehiculares
## Backend FastAPI - Documentación para Cursor AI

> **Versión:** 1.0.0  
> **Última actualización:** Diciembre 2024  
> **Stack:** FastAPI + PostgreSQL + SQLAlchemy + Celery + Redis + Docker

---

# PARTE 1: ARQUITECTURA Y SETUP INICIAL

## 📋 Tabla de Contenidos

1. [Visión General del Sistema](#visión-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Setup Inicial](#setup-inicial)
5. [Modelo de Datos](#modelo-de-datos)
6. [Sistema de Permisos](#sistema-de-permisos)
7. [Configuración](#configuración)
8. [Endpoints API](#endpoints-api)
9. [Celery Tasks](#celery-tasks)
10. [Testing](#testing)
11. [Deployment](#deployment)

---

## 1. Visión General del Sistema

### 1.1 Descripción
Sistema backend para gestión de oficios e investigaciones vehiculares para estudios jurídicos y empresas de cobranza. Permite:

- **Gestión de Buffets** (estudios jurídicos clientes)
- **Gestión de Usuarios** (3 roles: Admin, Investigador, Cliente)
- **Gestión de Oficios** (casos de investigación vehicular)
- **Investigaciones** (consultas a APIs, terreno, llamadas)
- **Notificaciones** (email a receptores judiciales)
- **Dashboard público** (para clientes con token)

### 1.2 Casos de Uso Principales

**Flujo típico:**
1. Admin crea buffet y usuario cliente
2. Investigador crea oficio desde Excel
3. Sistema consulta APIs automáticamente (Celery)
4. Investigador agrega direcciones adicionales
5. Investigador encuentra vehículo en terreno
6. Investigador sube fotos
7. Sistema notifica a receptor judicial
8. Cliente ve progreso en dashboard público

### 1.3 Roles y Permisos

```
ADMIN
├── Gestionar buffets (CRUD)
├── Gestionar usuarios (CRUD)
├── Ver todos los oficios
└── Acceso completo al sistema

INVESTIGADOR
├── Crear oficios
├── Editar oficios
├── Agregar direcciones/propietarios
├── Subir adjuntos
├── Consultar APIs
├── Notificar receptor
└── Ver todos los oficios (colaborativo)

CLIENTE (Usuario Buffet)
├── Ver dashboard público (con token)
├── Ver solo oficios de su buffet
└── Solo lectura (no puede modificar)
```

---

## 2. Estructura del Proyecto

### 2.1 Árbol de Directorios

```
backend/
│
├── src/                                    # Código fuente
│   ├── core/                               # Configuración y utilidades centrales
│   │   ├── __init__.py
│   │   ├── config.py                       # Settings (Pydantic Settings)
│   │   ├── security.py                     # JWT, password hashing, auth
│   │   └── permissions.py                  # RBAC decorators
│   │
│   ├── infrastructure/                     # Capa de infraestructura
│   │   ├── __init__.py
│   │   └── database/
│   │       ├── __init__.py
│   │       ├── models.py                   # SQLAlchemy models (10 tablas)
│   │       └── session.py                  # DB session management
│   │
│   ├── presentation/                       # Capa de presentación (API REST)
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/                         # API version 1
│   │   │       ├── __init__.py
│   │   │       ├── auth.py                 # Login, JWT tokens
│   │   │       ├── buffets.py              # CRUD buffets
│   │   │       ├── usuarios.py             # CRUD usuarios
│   │   │       └── oficios.py              # CRUD oficios + relaciones
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── schemas.py                  # Pydantic request/response schemas
│   │
│   ├── tasks/                              # Celery async tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py                   # Celery configuration
│   │   ├── api_consultas.py                # API integrations (Boostr, etc)
│   │   └── notificaciones.py               # Email notifications
│   │
│   └── main.py                             # FastAPI app entry point
│
├── scripts/                                # Utility scripts
│   └── init_db.py                          # Initialize DB with test data
│
├── storage/                                # File storage (local/S3)
│   └── oficios/
│       └── .gitkeep
│
├── tests/                                  # Tests
│   ├── __init__.py
│   ├── conftest.py                         # Pytest fixtures
│   ├── test_auth.py
│   ├── test_buffets.py
│   ├── test_usuarios.py
│   └── test_oficios.py
│
├── alembic/                                # Database migrations
│   ├── versions/                           # Migration files
│   ├── env.py                              # Alembic environment
│   └── alembic.ini                         # Alembic configuration
│
├── .env                                    # Environment variables (DO NOT COMMIT)
├── .env.example                            # Environment template
├── .gitignore                              # Git ignore rules
├── requirements.txt                        # Python dependencies
├── Dockerfile                              # Docker image definition
├── docker-compose.yml                      # Multi-container Docker setup
├── Makefile                                # Developer commands
└── README.md                               # Project documentation
```

### 2.2 Arquitectura de Capas (Clean Architecture)

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION                          │
│  (FastAPI Routes, Schemas, Dependencies)                │
│  • src/presentation/api/v1/*.py                         │
│  • src/presentation/schemas/schemas.py                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                      CORE                                │
│  (Business Logic, Security, Configuration)              │
│  • src/core/config.py                                   │
│  • src/core/security.py                                 │
│  • src/core/permissions.py                              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE                          │
│  (Database, External APIs, Storage)                     │
│  • src/infrastructure/database/models.py                │
│  • src/infrastructure/database/session.py               │
│  • src/tasks/*.py (Celery workers)                      │
└─────────────────────────────────────────────────────────┘
```

**Principios:**
- **Presentation Layer:** Maneja HTTP, validación de entrada, serialización
- **Core Layer:** Lógica de negocio, reglas de seguridad, configuración
- **Infrastructure Layer:** Acceso a datos, integraciones externas, I/O

---

## 3. Stack Tecnológico

### 3.1 Backend Core

```python
# Framework Web
fastapi==0.109.0          # Framework async moderno
uvicorn[standard]==0.27.0 # ASGI server

# Validación y Settings
pydantic==2.5.3           # Data validation
pydantic-settings==2.1.0  # Settings management

# Database
sqlalchemy==2.0.25        # ORM
alembic==1.13.1          # Migrations
psycopg2-binary==2.9.9   # PostgreSQL driver

# Authentication
python-jose[cryptography]==3.3.0  # JWT tokens
passlib[bcrypt]==1.7.4            # Password hashing

# Async Tasks
celery==5.3.6            # Distributed task queue
redis==5.0.1             # Message broker
flower==2.0.1            # Celery monitoring

# Email
aiosmtplib==3.0.1        # Async SMTP client
jinja2==3.1.3            # Email templates

# Storage
boto3==1.34.34           # AWS S3 (optional)
pillow==10.2.0           # Image processing

# HTTP Client
httpx==0.26.0            # Async HTTP client
requests==2.31.0         # Sync HTTP client

# Excel Processing
pandas==2.2.0            # Data manipulation
openpyxl==3.1.2          # Excel files

# Development
pytest==7.4.4            # Testing
black==24.1.1            # Code formatting
ruff==0.1.14             # Linting
mypy==1.8.0              # Type checking
```

### 3.2 Infraestructura

```yaml
# Docker Services
services:
  - api:        FastAPI application
  - db:         PostgreSQL 16
  - redis:      Redis 7 (Celery broker)
  - celery:     Celery worker
  - beat:       Celery beat (scheduler)
  - flower:     Celery monitoring UI

# Puertos
- 8000: API (FastAPI)
- 5432: PostgreSQL
- 6379: Redis
- 5555: Flower (Celery monitor)
```

### 3.3 Herramientas de Desarrollo

```bash
# Code Quality
make format      # Black (code formatting)
make lint        # Ruff (linting)
make type-check  # Mypy (type checking)
make test        # Pytest (testing)

# Development
make dev         # Start development environment
make logs        # View API logs
make shell       # Access container shell
make init-db     # Initialize database

# Database
make migration   # Create new migration
make migrate     # Apply migrations
make db-shell    # PostgreSQL shell
```

---

## 4. Setup Inicial

### 4.1 Prerequisitos

```bash
# Opción 1: Docker (Recomendado)
- Docker 20+
- Docker Compose 2+

# Opción 2: Local Development
- Python 3.11+
- PostgreSQL 16+
- Redis 7+
```

### 4.2 Instalación con Docker (5 minutos)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd backend

# 2. Crear estructura de carpetas
mkdir -p src/{core,infrastructure/database,presentation/{api/v1,schemas},tasks}
mkdir -p scripts tests storage/oficios alembic/versions

# 3. Crear archivos __init__.py
touch src/__init__.py
touch src/core/__init__.py
touch src/infrastructure/__init__.py
touch src/infrastructure/database/__init__.py
touch src/presentation/__init__.py
touch src/presentation/api/__init__.py
touch src/presentation/api/v1/__init__.py
touch src/presentation/schemas/__init__.py
touch src/tasks/__init__.py
touch tests/__init__.py
touch storage/oficios/.gitkeep

# 4. Copiar variables de entorno
cp .env.example .env

# 5. Iniciar servicios
docker-compose up -d

# 6. Inicializar base de datos
docker-compose exec api python scripts/init_db.py

# 7. Verificar
curl http://localhost:8000/health
# Respuesta: {"status":"healthy"}
```

### 4.3 Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar PostgreSQL
# Crear base de datos
createdb investigaciones_db

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores locales

# 5. Inicializar base de datos
python scripts/init_db.py

# 6. Iniciar API
uvicorn src.main:app --reload

# 7. En otra terminal: Celery worker
celery -A src.tasks.celery_app worker --loglevel=info

# 8. En otra terminal: Celery beat (opcional)
celery -A src.tasks.celery_app beat --loglevel=info

# 9. En otra terminal: Flower (opcional)
celery -A src.tasks.celery_app flower --port=5555
```

### 4.4 Verificación de Instalación

```bash
# 1. Health check
curl http://localhost:8000/health
# {"status":"healthy"}

# 2. API documentation
open http://localhost:8000/docs

# 3. Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@investigaciones.cl","password":"admin123"}'

# Respuesta esperada:
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer",
#   "user": { ... }
# }

# 4. Verificar Celery (Flower)
open http://localhost:5555

# 5. Verificar servicios Docker
docker-compose ps
# Todos los servicios deben estar "Up"
```

### 4.5 Credenciales de Prueba

Después de ejecutar `init_db.py`:

```python
# Admin
email: "admin@investigaciones.cl"
password: "admin123"

# Investigador
email: "investigador@investigaciones.cl"
password: "inv123"

# Cliente (Buffet)
email: "cliente@buffetgonzalez.cl"
password: "cliente123"
buffet_id: 1
```

---

## 5. Modelo de Datos

### 5.1 Diagrama de Entidades

```
┌─────────────┐
│   BUFFET    │ (Estudio jurídico cliente)
│  id         │
│  nombre     │
│  rut        │
│  token      │──┐
└─────────────┘  │
       │         │
       │ 1       │ N
       │         │
       ↓         ↓
┌─────────────┐  ┌─────────────┐
│  USUARIO    │  │   OFICIO    │ (Caso de investigación)
│  id         │  │  id         │
│  email      │  │  numero     │
│  rol ───────┼──│  estado     │
│  buffet_id  │  │  buffet_id  │
└─────────────┘  │  inv_id     │
       │         └─────────────┘
       │ N              │
       │                │ 1:1
       ↓                ↓
┌─────────────┐  ┌─────────────┐
│INVESTIGACION│  │  VEHICULO   │
│  id         │  │  patente    │
│  oficio_id  │  │  marca      │
│  tipo       │  │  modelo     │
│  resultado  │  └─────────────┘
└─────────────┘         │
                        │ 1:N
                        ↓
                 ┌──────────────┐
                 │  PROPIETARIO │
                 │  rut         │
                 │  tipo        │
                 └──────────────┘
                        │ 1:N
                        ↓
                 ┌──────────────┐
                 │  DIRECCION   │
                 │  direccion   │
                 │  verificada  │
                 └──────────────┘
```

### 5.2 Tablas Detalladas

#### 5.2.1 Buffet (Entidad Cliente)

```python
class Buffet(Base):
    __tablename__ = "buffets"
    
    # Campos
    id: int                    # PK
    nombre: str                # "Buffet González y Asociados"
    rut: str                   # Unique, "76.123.456-7"
    email_principal: str
    telefono: str
    contacto_nombre: str
    token_tablero: str         # Unique, para acceso público
    activo: bool               # Soft delete
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    usuarios: List[Usuario]    # 1:N - Usuarios del buffet
    oficios: List[Oficio]      # 1:N - Oficios del buffet
```

**Validaciones:**
- `rut` debe ser único
- `token_tablero` se genera automáticamente: `secrets.token_urlsafe(32)`
- Al desactivar, `activo = False` (no se elimina)

**Ejemplo:**
```json
{
  "id": 1,
  "nombre": "Buffet González y Asociados",
  "rut": "76.123.456-7",
  "email_principal": "contacto@buffetgonzalez.cl",
  "telefono": "+56912345678",
  "token_tablero": "kJ9mP3nQ7rX2bY5cZ8wT1dF6hG4vN0aL",
  "activo": true
}
```

#### 5.2.2 Usuario (Admin, Investigador, Cliente)

```python
class Usuario(Base):
    __tablename__ = "usuarios"
    
    # Campos
    id: int                    # PK
    email: str                 # Unique
    nombre: str
    password_hash: str         # Bcrypt hash
    rol: RolEnum               # "admin" | "investigador" | "cliente"
    buffet_id: Optional[int]   # FK a Buffet (NULL para admin/investigador)
    activo: bool
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    buffet: Optional[Buffet]           # N:1 - Buffet del usuario (si es cliente)
    oficios_asignados: List[Oficio]    # 1:N - Oficios asignados (si es investigador)
    investigaciones: List[Investigacion]
    adjuntos: List[Adjunto]

# Enum de Roles
class RolEnum(str, Enum):
    ADMIN = "admin"
    INVESTIGADOR = "investigador"
    CLIENTE = "cliente"
```

**Validaciones:**
- `email` debe ser único
- Si `rol = "cliente"` → `buffet_id` es obligatorio
- Si `rol = "admin"` o `"investigador"` → `buffet_id` debe ser NULL
- `password_hash` se genera con: `passlib.hash.bcrypt.hash(password)`

**Ejemplo:**
```json
{
  "id": 1,
  "email": "investigador@investigaciones.cl",
  "nombre": "Carlos Investigador",
  "rol": "investigador",
  "buffet_id": null,
  "activo": true
}
```

---

**FIN PARTE 1/4**

Continuaré con la Parte 2 que incluirá:
- Resto del modelo de datos (Oficio, Vehiculo, Propietario, Direccion, etc.)
- Sistema de autenticación completo
- Configuración detallada

¿Continúo con la Parte 2?