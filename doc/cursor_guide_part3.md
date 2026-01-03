# PARTE 3: CONFIGURACIÓN Y ENDPOINTS API

## 8. Configuración (src/core/config.py)

### 8.1 Settings con Pydantic

```python
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    Uses Pydantic Settings for automatic validation and type conversion
    """
    
    # ==================== ENVIRONMENT ====================
    ENVIRONMENT: str = "development"  # development | staging | production
    APP_NAME: str = "Sistema de Investigaciones Vehiculares"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # ==================== DATABASE ====================
    DATABASE_URL: str  # Required
    # Example: postgresql://user:password@localhost:5432/dbname
    
    # Pool settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False  # Set to True to log all SQL queries
    
    # ==================== REDIS ====================
    REDIS_URL: str  # Required
    # Example: redis://localhost:6379/0
    
    # ==================== SECURITY ====================
    SECRET_KEY: str  # Required - min 32 characters
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",     # Next.js dev
        "http://localhost:3001",     # Alternative port
        "https://yourdomain.com",    # Production frontend
    ]
    
    # ==================== EMAIL (SMTP) ====================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@investigaciones.cl"
    SMTP_FROM_NAME: str = "Sistema Investigaciones"
    
    # Email templates
    EMAIL_TEMPLATES_DIR: str = "src/templates/email"
    
    # ==================== FILE STORAGE ====================
    STORAGE_TYPE: str = "local"  # local | s3
    STORAGE_PATH: str = "/app/storage"
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # AWS S3 (if STORAGE_TYPE=s3)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None  # For MinIO or other S3-compatible
    
    # ==================== EXTERNAL APIs ====================
    BOOSTR_API_URL: str = ""
    BOOSTR_API_KEY: str = ""
    BOOSTR_TIMEOUT: int = 30  # seconds
    
    # Other APIs
    MULTAS_API_URL: str = ""
    MULTAS_API_KEY: str = ""
    
    # ==================== CELERY ====================
    CELERY_BROKER_URL: Optional[str] = None  # Defaults to REDIS_URL
    CELERY_RESULT_BACKEND: Optional[str] = None  # Defaults to REDIS_URL
    CELERY_TASK_TIME_LIMIT: int = 300  # 5 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = 240  # 4 minutes
    
    # ==================== MONITORING ====================
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = "INFO"  # DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_FORMAT: str = "json"  # json | text
    
    # ==================== RATE LIMITING ====================
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ==================== PAGINATION ====================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Using lru_cache ensures settings are only loaded once
    
    Usage:
        from src.core.config import get_settings
        
        settings = get_settings()
        print(settings.DATABASE_URL)
    """
    return Settings()
```

### 8.2 Archivo .env

```bash
# ==================== ENVIRONMENT ====================
ENVIRONMENT=development
DEBUG=true

# ==================== DATABASE ====================
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/investigaciones_db

# ==================== REDIS ====================
REDIS_URL=redis://localhost:6379/0

# ==================== SECURITY ====================
# Generate with: openssl rand -hex 32
SECRET_KEY=your-super-secret-key-min-32-characters-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ==================== CORS ====================
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# ==================== EMAIL ====================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@investigaciones.cl

# ==================== STORAGE ====================
STORAGE_TYPE=local
STORAGE_PATH=/app/storage
MAX_FILE_SIZE=10485760

# AWS S3 (if STORAGE_TYPE=s3)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=investigaciones-adjuntos

# ==================== EXTERNAL APIs ====================
BOOSTR_API_URL=https://api.boostr.cl
BOOSTR_API_KEY=your-boostr-api-key

# ==================== MONITORING ====================
SENTRY_DSN=
LOG_LEVEL=INFO
```

---

## 9. Endpoints API Completos

### 9.1 Auth Endpoints

#### POST /api/v1/auth/login

```python
"""Login and get JWT token"""

# Request
{
    "email": "admin@investigaciones.cl",
    "password": "admin123"
}

# Response 200
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "email": "admin@investigaciones.cl",
        "nombre": "Admin Sistema",
        "rol": "admin",
        "buffet_id": null,
        "activo": true,
        "created_at": "2024-12-01T10:00:00"
    }
}

# Response 401 (Credenciales incorrectas)
{
    "detail": "Email o contraseña incorrectos"
}

# Response 403 (Usuario inactivo)
{
    "detail": "Usuario inactivo"
}
```

#### GET /api/v1/auth/me

```python
"""Get current user info"""

# Headers
Authorization: Bearer <token>

# Response 200
{
    "id": 1,
    "email": "admin@investigaciones.cl",
    "nombre": "Admin Sistema",
    "rol": "admin",
    "buffet_id": null,
    "activo": true,
    "avatar_url": null,
    "created_at": "2024-12-01T10:00:00"
}

# Response 401 (Token inválido)
{
    "detail": "Could not validate credentials"
}
```

### 9.2 Buffet Endpoints

#### POST /api/v1/buffets/ (Admin only)

```python
"""Create new buffet"""

# Headers
Authorization: Bearer <admin-token>

# Request
{
    "nombre": "Buffet González y Asociados",
    "rut": "76.123.456-7",
    "email_principal": "contacto@buffetgonzalez.cl",
    "telefono": "+56912345678",
    "contacto_nombre": "Juan González"
}

# Response 201
{
    "id": 1,
    "nombre": "Buffet González y Asociados",
    "rut": "76.123.456-7",
    "email_principal": "contacto@buffetgonzalez.cl",
    "telefono": "+56912345678",
    "contacto_nombre": "Juan González",
    "token_tablero": "kJ9mP3nQ7rX2bY5cZ8wT1dF6hG4vN0aL",  # Auto-generated
    "activo": true,
    "created_at": "2024-12-01T10:00:00"
}

# Response 400 (RUT duplicado)
{
    "detail": "Ya existe un buffet con este RUT"
}

# Response 403 (No es admin)
{
    "detail": "Permisos insuficientes. Se requiere rol de administrador."
}
```

#### GET /api/v1/buffets/ (Admin only)

```python
"""List buffets with pagination"""

# Headers
Authorization: Bearer <admin-token>

# Query params
?skip=0&limit=20&activo=true

# Response 200
[
    {
        "id": 1,
        "nombre": "Buffet González y Asociados",
        "rut": "76.123.456-7",
        "email_principal": "contacto@buffetgonzalez.cl",
        "telefono": "+56912345678",
        "token_tablero": "kJ9mP3nQ7rX2bY5cZ8wT1dF6hG4vN0aL",
        "activo": true,
        "created_at": "2024-12-01T10:00:00"
    },
    {
        "id": 2,
        "nombre": "Buffet Pérez & Cia",
        "rut": "76.987.654-3",
        "email_principal": "contacto@buffetperez.cl",
        "telefono": "+56987654321",
        "token_tablero": "aB1cD2eF3gH4iJ5kL6mN7oP8qR9sT0uV",
        "activo": true,
        "created_at": "2024-12-02T11:00:00"
    }
]
```

#### GET /api/v1/buffets/{id} (Admin only)

```python
"""Get buffet by ID"""

# Headers
Authorization: Bearer <admin-token>

# Response 200
{
    "id": 1,
    "nombre": "Buffet González y Asociados",
    "rut": "76.123.456-7",
    "email_principal": "contacto@buffetgonzalez.cl",
    "telefono": "+56912345678",
    "contacto_nombre": "Juan González",
    "token_tablero": "kJ9mP3nQ7rX2bY5cZ8wT1dF6hG4vN0aL",
    "activo": true,
    "created_at": "2024-12-01T10:00:00"
}

# Response 404
{
    "detail": "Buffet no encontrado"
}
```

#### PATCH /api/v1/buffets/{id} (Admin only)

```python
"""Update buffet"""

# Headers
Authorization: Bearer <admin-token>

# Request (all fields optional)
{
    "nombre": "Buffet González & Asociados SpA",
    "email_principal": "nuevo@buffetgonzalez.cl",
    "telefono": "+56911111111"
}

# Response 200
{
    "id": 1,
    "nombre": "Buffet González & Asociados SpA",  # Updated
    "rut": "76.123.456-7",
    "email_principal": "nuevo@buffetgonzalez.cl",  # Updated
    "telefono": "+56911111111",  # Updated
    "contacto_nombre": "Juan González",
    "token_tablero": "kJ9mP3nQ7rX2bY5cZ8wT1dF6hG4vN0aL",
    "activo": true,
    "created_at": "2024-12-01T10:00:00"
}
```

#### DELETE /api/v1/buffets/{id} (Admin only)

```python
"""Deactivate buffet (soft delete)"""

# Headers
Authorization: Bearer <admin-token>

# Response 204 No Content
# (Empty body)

# Note: Buffet is not deleted from DB, just marked as activo=false
```

#### GET /api/v1/buffets/{id}/usuarios (Admin only)

```python
"""List users of a buffet"""

# Headers
Authorization: Bearer <admin-token>

# Response 200
[
    {
        "id": 3,
        "email": "cliente@buffetgonzalez.cl",
        "nombre": "Juan Pérez",
        "rol": "cliente",
        "buffet_id": 1,
        "activo": true,
        "created_at": "2024-12-01T12:00:00"
    },
    {
        "id": 4,
        "email": "maria@buffetgonzalez.cl",
        "nombre": "María López",
        "rol": "cliente",
        "buffet_id": 1,
        "activo": true,
        "created_at": "2024-12-02T09:00:00"
    }
]
```

### 9.3 Usuario Endpoints

#### POST /api/v1/usuarios/ (Admin only)

```python
"""Create new user"""

# Headers
Authorization: Bearer <admin-token>

# Request
{
    "email": "nuevo@example.com",
    "nombre": "Usuario Nuevo",
    "password": "password123",
    "rol": "investigador",
    "buffet_id": null  # Required if rol="cliente", null otherwise
}

# Response 201
{
    "id": 5,
    "email": "nuevo@example.com",
    "nombre": "Usuario Nuevo",
    "rol": "investigador",
    "buffet_id": null,
    "activo": true,
    "avatar_url": null,
    "created_at": "2024-12-21T15:00:00"
}

# Response 400 (Email duplicado)
{
    "detail": "Ya existe un usuario con este email"
}

# Response 422 (Validación fallida)
{
    "detail": [
        {
            "loc": ["body", "buffet_id"],
            "msg": "buffet_id es requerido para usuarios con rol cliente",
            "type": "value_error"
        }
    ]
}
```

#### GET /api/v1/usuarios/ (Admin only)

```python
"""List users with filters"""

# Headers
Authorization: Bearer <admin-token>

# Query params
?skip=0&limit=20&rol=investigador&activo=true

# Response 200
[
    {
        "id": 2,
        "email": "investigador@investigaciones.cl",
        "nombre": "Carlos Investigador",
        "rol": "investigador",
        "buffet_id": null,
        "activo": true,
        "created_at": "2024-12-01T10:00:00"
    },
    {
        "id": 5,
        "email": "nuevo@example.com",
        "nombre": "Usuario Nuevo",
        "rol": "investigador",
        "buffet_id": null,
        "activo": true,
        "created_at": "2024-12-21T15:00:00"
    }
]
```

#### GET /api/v1/usuarios/me

```python
"""Get current user (same as /auth/me)"""

# Headers
Authorization: Bearer <token>

# Response 200
{
    "id": 1,
    "email": "admin@investigaciones.cl",
    "nombre": "Admin Sistema",
    "rol": "admin",
    "buffet_id": null,
    "activo": true,
    "avatar_url": null,
    "created_at": "2024-12-01T10:00:00"
}
```

#### PATCH /api/v1/usuarios/{id} (Admin only)

```python
"""Update user"""

# Headers
Authorization: Bearer <admin-token>

# Request (all fields optional)
{
    "nombre": "Carlos Investigador Principal",
    "email": "carlos@investigaciones.cl",
    "password": "newpassword123",  # Optional - will be hashed
    "activo": true,
    "avatar_url": "https://example.com/avatar.jpg"
}

# Response 200
{
    "id": 2,
    "email": "carlos@investigaciones.cl",  # Updated
    "nombre": "Carlos Investigador Principal",  # Updated
    "rol": "investigador",
    "buffet_id": null,
    "activo": true,
    "avatar_url": "https://example.com/avatar.jpg",  # Updated
    "created_at": "2024-12-01T10:00:00"
}
```

#### PATCH /api/v1/usuarios/{id}/cambiar-rol (Admin only)

```python
"""Change user role"""

# Headers
Authorization: Bearer <admin-token>

# Request
{
    "rol": "cliente",
    "buffet_id": 1  # Required if changing to "cliente"
}

# Response 200
{
    "id": 5,
    "email": "nuevo@example.com",
    "nombre": "Usuario Nuevo",
    "rol": "cliente",  # Changed
    "buffet_id": 1,  # Changed
    "activo": true,
    "avatar_url": null,
    "created_at": "2024-12-21T15:00:00"
}

# Response 400 (Validación)
{
    "detail": "buffet_id es requerido para rol cliente"
}
```

#### DELETE /api/v1/usuarios/{id} (Admin only)

```python
"""Deactivate user (soft delete)"""

# Headers
Authorization: Bearer <admin-token>

# Response 204 No Content
# (Empty body)

# Note: User is not deleted, just marked as activo=false
```

### 9.4 Oficio Endpoints

#### POST /api/v1/oficios/ (Admin/Investigador)

```python
"""Create new oficio with vehicle, owner, and address"""

# Headers
Authorization: Bearer <investigador-token>

# Request
{
    "numero_oficio": "OF-2024-001",
    "buffet_id": 1,
    "prioridad": "media",
    "fecha_limite": "2024-12-31",
    "notas_generales": "Oficio urgente - cliente VIP",
    
    // Vehicle data
    "patente": "ABCD12",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2020,
    "color": "Blanco",
    "vin": "1HGBH41JXMN109186",
    
    // Main owner
    "propietario_rut": "12345678-9",
    "propietario_nombre": "Juan Pérez González",
    "propietario_email": "juan@example.com",
    "propietario_telefono": "+56912345678",
    
    // Main address
    "direccion": "Av. Principal 123, Depto 501",
    "comuna": "Santiago",
    "region": "Metropolitana"
}

# Response 201
{
    "id": 1,
    "numero_oficio": "OF-2024-001",
    "buffet_id": 1,
    "investigador_id": null,  // Not assigned yet
    "estado": "pendiente",
    "prioridad": "media",
    "fecha_ingreso": "2024-12-21",  // Auto-set to today
    "fecha_limite": "2024-12-31",
    "notas_generales": "Oficio urgente - cliente VIP",
    "created_at": "2024-12-21T15:00:00",
    "updated_at": "2024-12-21T15:00:00",
    "vehiculo": {
        "id": 1,
        "patente": "ABCD12",
        "marca": "Toyota",
        "modelo": "Corolla",
        "año": 2020,
        "color": "Blanco",
        "vin": "1HGBH41JXMN109186"
    }
}

# Response 400 (Número de oficio duplicado)
{
    "detail": "Ya existe un oficio con este número"
}

# Response 403 (No es admin/investigador)
{
    "detail": "Permisos insuficientes. Se requiere rol de investigador o administrador."
}
```

#### GET /api/v1/oficios/

```python
"""List oficios with filters and pagination"""

# Headers
Authorization: Bearer <token>

# Query params
?skip=0&limit=20&estado=investigacion&buffet_id=1&investigador_id=2

# Response 200 (Admin/Investigador - ven todos)
[
    {
        "id": 1,
        "numero_oficio": "OF-2024-001",
        "buffet_id": 1,
        "investigador_id": 2,
        "estado": "investigacion",
        "prioridad": "alta",
        "fecha_ingreso": "2024-12-01",
        "fecha_limite": "2024-12-15",
        "notas_generales": "Cliente VIP",
        "created_at": "2024-12-01T10:00:00",
        "updated_at": "2024-12-02T14:30:00",
        "vehiculo": {
            "id": 1,
            "patente": "ABCD12",
            "marca": "Toyota",
            "modelo": "Corolla",
            "año": 2020,
            "color": "Blanco",
            "vin": "1HGBH41JXMN109186"
        }
    },
    // ... more oficios
]

# Response 200 (Cliente - solo ve oficios de su buffet)
[
    {
        "id": 1,
        "numero_oficio": "OF-2024-001",
        "buffet_id": 1,  // Su buffet
        "investigador_id": 2,
        "estado": "investigacion",
        // ... resto de campos
    }
]
```

#### GET /api/v1/oficios/{id}

```python
"""Get oficio by ID"""

# Headers
Authorization: Bearer <token>

# Response 200
{
    "id": 1,
    "numero_oficio": "OF-2024-001",
    "buffet_id": 1,
    "investigador_id": 2,
    "estado": "investigacion",
    "prioridad": "alta",
    "fecha_ingreso": "2024-12-01",
    "fecha_limite": "2024-12-15",
    "notas_generales": "Cliente VIP - prioridad máxima",
    "created_at": "2024-12-01T10:00:00",
    "updated_at": "2024-12-02T14:30:00",
    "vehiculo": {
        "id": 1,
        "patente": "ABCD12",
        "marca": "Toyota",
        "modelo": "Corolla",
        "año": 2020,
        "color": "Blanco",
        "vin": "1HGBH41JXMN109186"
    }
}

# Response 403 (Cliente intentando ver oficio de otro buffet)
{
    "detail": "No tiene acceso a este oficio"
}

# Response 404
{
    "detail": "Oficio no encontrado"
}
```

---

**FIN PARTE 3/4**

Continuaré con la Parte 4 final que incluirá:
- Más endpoints (direcciones, propietarios, adjuntos)
- Celery tasks completos
- Testing
- Deployment
- Comandos útiles

¿Continúo con la Parte 4 final?