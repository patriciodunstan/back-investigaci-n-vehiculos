# PARTE 5: SHARED KERNEL, CORE Y SETUP INICIAL

> **Prerrequisito:** Haber leído las Partes 1-4  
> **Objetivo:** Crear la base del proyecto con arquitectura modular  
> **Tiempo estimado:** 1-2 horas

---

## 1. Estructura de Carpetas Inicial

Primero, crea toda la estructura de carpetas. En Windows PowerShell:

```powershell
# Desde la raíz del proyecto: C:\Users\patriciods\back-investigación-vehiculos

# Crear estructura principal
mkdir -p src/core
mkdir -p src/shared/domain/value_objects
mkdir -p src/shared/domain/entities
mkdir -p src/shared/domain/exceptions
mkdir -p src/shared/application/interfaces
mkdir -p src/shared/application/events
mkdir -p src/shared/infrastructure/database
mkdir -p src/shared/infrastructure/event_bus
mkdir -p src/shared/presentation/middleware
mkdir -p src/shared/presentation/dependencies

# Crear estructura de módulos (vacíos por ahora)
mkdir -p src/modules/usuarios/domain/entities
mkdir -p src/modules/usuarios/domain/value_objects
mkdir -p src/modules/usuarios/domain/exceptions
mkdir -p src/modules/usuarios/application/interfaces
mkdir -p src/modules/usuarios/application/use_cases
mkdir -p src/modules/usuarios/application/dtos
mkdir -p src/modules/usuarios/infrastructure/models
mkdir -p src/modules/usuarios/infrastructure/repositories
mkdir -p src/modules/usuarios/presentation

mkdir -p src/modules/buffets/domain/entities
mkdir -p src/modules/buffets/domain/value_objects
mkdir -p src/modules/buffets/domain/exceptions
mkdir -p src/modules/buffets/application/interfaces
mkdir -p src/modules/buffets/application/use_cases
mkdir -p src/modules/buffets/application/dtos
mkdir -p src/modules/buffets/infrastructure/models
mkdir -p src/modules/buffets/infrastructure/repositories
mkdir -p src/modules/buffets/presentation

mkdir -p src/modules/oficios/domain/entities
mkdir -p src/modules/oficios/domain/value_objects
mkdir -p src/modules/oficios/domain/exceptions
mkdir -p src/modules/oficios/application/interfaces
mkdir -p src/modules/oficios/application/use_cases
mkdir -p src/modules/oficios/application/dtos
mkdir -p src/modules/oficios/infrastructure/models
mkdir -p src/modules/oficios/infrastructure/repositories
mkdir -p src/modules/oficios/presentation

mkdir -p src/modules/investigaciones/domain/entities
mkdir -p src/modules/investigaciones/application/interfaces
mkdir -p src/modules/investigaciones/application/use_cases
mkdir -p src/modules/investigaciones/infrastructure/models
mkdir -p src/modules/investigaciones/infrastructure/repositories
mkdir -p src/modules/investigaciones/presentation

mkdir -p src/modules/notificaciones/domain/entities
mkdir -p src/modules/notificaciones/application/interfaces
mkdir -p src/modules/notificaciones/application/use_cases
mkdir -p src/modules/notificaciones/application/handlers
mkdir -p src/modules/notificaciones/infrastructure/models
mkdir -p src/modules/notificaciones/infrastructure/repositories
mkdir -p src/modules/notificaciones/infrastructure/email
mkdir -p src/modules/notificaciones/presentation

# Otras carpetas
mkdir -p tasks/workers
mkdir -p tests/unit/shared
mkdir -p tests/unit/modules
mkdir -p tests/integration
mkdir -p alembic/versions
mkdir -p storage/oficios
mkdir -p scripts
```

---

## 2. Archivos __init__.py

Crea archivos `__init__.py` vacíos en todas las carpetas de Python:

```powershell
# Archivos __init__.py principales
New-Item -ItemType File -Path src/__init__.py -Force
New-Item -ItemType File -Path src/core/__init__.py -Force

# Shared
New-Item -ItemType File -Path src/shared/__init__.py -Force
New-Item -ItemType File -Path src/shared/domain/__init__.py -Force
New-Item -ItemType File -Path src/shared/domain/value_objects/__init__.py -Force
New-Item -ItemType File -Path src/shared/domain/entities/__init__.py -Force
New-Item -ItemType File -Path src/shared/domain/exceptions/__init__.py -Force
New-Item -ItemType File -Path src/shared/application/__init__.py -Force
New-Item -ItemType File -Path src/shared/application/interfaces/__init__.py -Force
New-Item -ItemType File -Path src/shared/application/events/__init__.py -Force
New-Item -ItemType File -Path src/shared/infrastructure/__init__.py -Force
New-Item -ItemType File -Path src/shared/infrastructure/database/__init__.py -Force
New-Item -ItemType File -Path src/shared/infrastructure/event_bus/__init__.py -Force
New-Item -ItemType File -Path src/shared/presentation/__init__.py -Force
New-Item -ItemType File -Path src/shared/presentation/middleware/__init__.py -Force
New-Item -ItemType File -Path src/shared/presentation/dependencies/__init__.py -Force

# Modules
New-Item -ItemType File -Path src/modules/__init__.py -Force
 New-Item -ItemType File -Path src\modules\usuarios\application\dtos\__init__.py -Force  

# (Repite para cada módulo - usuarios, buffets, oficios, investigaciones, notificaciones)
# Te daré un script completo más adelante
```

---

## 3. Requirements.txt

**Archivo:** `requirements.txt` (en la raíz del proyecto)

```txt
# ==================== FRAMEWORK WEB ====================
fastapi==0.109.0
uvicorn[standard]==0.27.0

# ==================== VALIDACIÓN Y SETTINGS ====================
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# ==================== DATABASE ====================
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# ==================== AUTENTICACIÓN ====================
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# ==================== ASYNC TASKS ====================
celery==5.3.6
redis==5.0.1
flower==2.0.1

# ==================== EMAIL ====================
aiosmtplib==3.0.1
jinja2==3.1.3

# ==================== HTTP CLIENT ====================
httpx==0.26.0

# ==================== STORAGE ====================
boto3==1.34.34
pillow==10.2.0

# ==================== EXCEL ====================
pandas==2.2.0
openpyxl==3.1.2

# ==================== DESARROLLO ====================
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
black==24.1.1
ruff==0.1.14
mypy==1.8.0
httpx==0.26.0

# ==================== UTILITIES ====================
python-multipart==0.0.6
python-dotenv==1.0.0
```

---

## 4. Archivo .env.example

**Archivo:** `.env.example` (en la raíz del proyecto)

```env
# ==================== ENVIRONMENT ====================
ENVIRONMENT=development
DEBUG=true
APP_NAME=Sistema de Investigaciones Vehiculares

# ==================== DATABASE ====================
# Para Docker: postgresql://postgres:postgres@db:5432/investigaciones_db
# Para local: postgresql://postgres:postgres@localhost:5432/investigaciones_db
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/investigaciones_db

# ==================== REDIS ====================
REDIS_URL=redis://localhost:6379/0

# ==================== SECURITY ====================
# IMPORTANTE: Genera tu propia clave con: openssl rand -hex 32
SECRET_KEY=tu-clave-secreta-de-al-menos-32-caracteres-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ==================== CORS ====================
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# ==================== EMAIL (SMTP) ====================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@investigaciones.cl
SMTP_FROM_NAME=Sistema Investigaciones

# ==================== STORAGE ====================
STORAGE_TYPE=local
STORAGE_PATH=./storage
MAX_FILE_SIZE=10485760

# ==================== EXTERNAL APIs ====================
BOOSTR_API_URL=
BOOSTR_API_KEY=

# ==================== LOGGING ====================
LOG_LEVEL=INFO
```

---

## 5. Core - Configuración

### 5.1 src/core/config.py

```python
"""
Configuración centralizada de la aplicación.

Usa Pydantic Settings para:
- Cargar variables de entorno
- Validar tipos automáticamente
- Proporcionar valores por defecto

Principios aplicados:
- SRP: Solo maneja configuración
- DIP: Las clases dependen de Settings, no de os.environ directamente
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Settings de la aplicación cargados desde variables de entorno.
    
    Attributes:
        ENVIRONMENT: Ambiente de ejecución (development, staging, production)
        DEBUG: Modo debug activo
        APP_NAME: Nombre de la aplicación
    """
    
    # ==================== ENVIRONMENT ====================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Sistema de Investigaciones Vehiculares"
    API_V1_STR: str = "/api/v1"
    
    # ==================== DATABASE ====================
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False  # True para ver SQL queries en logs
    
    # ==================== REDIS ====================
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ==================== SECURITY ====================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==================== CORS ====================
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # ==================== EMAIL ====================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@investigaciones.cl"
    SMTP_FROM_NAME: str = "Sistema Investigaciones"
    
    # ==================== STORAGE ====================
    STORAGE_TYPE: str = "local"  # local | s3
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "application/pdf",
    ]
    
    # S3 (opcional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # ==================== EXTERNAL APIs ====================
    BOOSTR_API_URL: str = ""
    BOOSTR_API_KEY: str = ""
    BOOSTR_TIMEOUT: int = 30
    
    # ==================== CELERY ====================
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = "INFO"
    
    # ==================== PAGINATION ====================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    @property
    def celery_broker(self) -> str:
        """URL del broker de Celery (usa REDIS_URL si no está definido)"""
        return self.CELERY_BROKER_URL or self.REDIS_URL
    
    @property
    def celery_backend(self) -> str:
        """URL del backend de resultados de Celery"""
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL
    
    @property
    def is_development(self) -> bool:
        """Verifica si estamos en ambiente de desarrollo"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Verifica si estamos en ambiente de producción"""
        return self.ENVIRONMENT == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene instancia cacheada de Settings.
    
    Usar @lru_cache asegura que Settings se cargue solo una vez,
    mejorando el rendimiento.
    
    Returns:
        Settings: Instancia de configuración
        
    Example:
        >>> from src.core.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.DATABASE_URL)
    """
    return Settings()
```

---

## 6. Shared Domain - Value Objects

Los Value Objects son objetos inmutables que representan conceptos del dominio. No tienen identidad, solo valor.

### 6.1 src/shared/domain/value_objects/rut.py

```python
"""
Value Object: RUT Chileno

Representa un RUT (Rol Único Tributario) chileno con validación del dígito verificador.

Principios aplicados:
- Inmutabilidad: Una vez creado, no puede modificarse
- Validación en construcción: Si el RUT es inválido, falla al crear
- Encapsulamiento: La lógica de validación está contenida en la clase
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)  # frozen=True hace la clase inmutable
class RutChileno:
    """
    Value Object para RUT chileno.
    
    Attributes:
        valor: RUT completo con formato (ej: "12.345.678-9")
        numero: Parte numérica sin puntos (ej: 12345678)
        digito_verificador: Dígito verificador (ej: "9" o "K")
    
    Example:
        >>> rut = RutChileno.crear("12345678-9")
        >>> print(rut.valor)  # "12.345.678-9"
        >>> print(rut.numero)  # 12345678
    """
    
    valor: str
    numero: int
    digito_verificador: str
    
    @classmethod
    def crear(cls, rut_string: str) -> "RutChileno":
        """
        Factory method para crear un RUT validado.
        
        Args:
            rut_string: RUT en cualquier formato ("12345678-9", "12.345.678-9", etc.)
            
        Returns:
            RutChileno: Instancia validada
            
        Raises:
            ValueError: Si el RUT es inválido
            
        Example:
            >>> rut = RutChileno.crear("12345678-9")
        """
        # Limpiar el RUT (quitar puntos, espacios, guiones)
        rut_limpio = cls._limpiar(rut_string)
        
        if not rut_limpio:
            raise ValueError("RUT no puede estar vacío")
        
        # Separar número y dígito verificador
        numero_str = rut_limpio[:-1]
        digito = rut_limpio[-1].upper()
        
        # Validar que el número sea numérico
        if not numero_str.isdigit():
            raise ValueError(f"RUT inválido: {rut_string}")
        
        numero = int(numero_str)
        
        # Validar dígito verificador
        digito_calculado = cls._calcular_digito_verificador(numero)
        if digito != digito_calculado:
            raise ValueError(
                f"Dígito verificador inválido para RUT {rut_string}. "
                f"Esperado: {digito_calculado}, Recibido: {digito}"
            )
        
        # Formatear con puntos y guión
        valor_formateado = cls._formatear(numero, digito)
        
        return cls(
            valor=valor_formateado,
            numero=numero,
            digito_verificador=digito
        )
    
    @classmethod
    def crear_sin_validar(cls, rut_string: str) -> "RutChileno":
        """
        Crea un RUT sin validar el dígito verificador.
        
        Útil para datos históricos o de prueba.
        
        Args:
            rut_string: RUT en cualquier formato
            
        Returns:
            RutChileno: Instancia sin validación de DV
        """
        rut_limpio = cls._limpiar(rut_string)
        numero_str = rut_limpio[:-1]
        digito = rut_limpio[-1].upper()
        numero = int(numero_str) if numero_str.isdigit() else 0
        valor_formateado = cls._formatear(numero, digito)
        
        return cls(
            valor=valor_formateado,
            numero=numero,
            digito_verificador=digito
        )
    
    @staticmethod
    def _limpiar(rut: str) -> str:
        """Elimina puntos, guiones y espacios del RUT"""
        return re.sub(r"[.\-\s]", "", rut.strip())
    
    @staticmethod
    def _calcular_digito_verificador(numero: int) -> str:
        """
        Calcula el dígito verificador usando el algoritmo módulo 11.
        
        Args:
            numero: Parte numérica del RUT
            
        Returns:
            str: Dígito verificador ("0"-"9" o "K")
        """
        suma = 0
        multiplicador = 2
        
        # Recorrer dígitos de derecha a izquierda
        for digito in reversed(str(numero)):
            suma += int(digito) * multiplicador
            multiplicador = multiplicador + 1 if multiplicador < 7 else 2
        
        resto = suma % 11
        resultado = 11 - resto
        
        if resultado == 11:
            return "0"
        elif resultado == 10:
            return "K"
        else:
            return str(resultado)
    
    @staticmethod
    def _formatear(numero: int, digito: str) -> str:
        """Formatea el RUT con puntos y guión (ej: 12.345.678-9)"""
        numero_str = str(numero)
        # Agregar puntos cada 3 dígitos desde la derecha
        partes = []
        while numero_str:
            partes.append(numero_str[-3:])
            numero_str = numero_str[:-3]
        numero_formateado = ".".join(reversed(partes))
        return f"{numero_formateado}-{digito}"
    
    def sin_formato(self) -> str:
        """Retorna el RUT sin puntos ni guión (ej: 123456789)"""
        return f"{self.numero}{self.digito_verificador}"
    
    def __str__(self) -> str:
        return self.valor
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RutChileno):
            return False
        return self.numero == other.numero


# Función de utilidad para validar RUT sin crear objeto
def es_rut_valido(rut_string: str) -> bool:
    """
    Verifica si un RUT es válido sin lanzar excepción.
    
    Args:
        rut_string: RUT a validar
        
    Returns:
        bool: True si el RUT es válido
        
    Example:
        >>> es_rut_valido("12345678-9")
        True
        >>> es_rut_valido("12345678-0")
        False
    """
    try:
        RutChileno.crear(rut_string)
        return True
    except ValueError:
        return False
```

### 6.2 src/shared/domain/value_objects/email.py

```python
"""
Value Object: Email

Representa una dirección de email validada.

Principios aplicados:
- Inmutabilidad
- Validación en construcción
- Normalización automática (lowercase)
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """
    Value Object para direcciones de email.
    
    Attributes:
        valor: Email normalizado (lowercase)
        usuario: Parte antes del @
        dominio: Parte después del @
        
    Example:
        >>> email = Email.crear("Usuario@Example.COM")
        >>> print(email.valor)  # "usuario@example.com"
    """
    
    valor: str
    usuario: str
    dominio: str
    
    # Patrón regex para validar email (simplificado pero efectivo)
    _PATRON_EMAIL = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    
    @classmethod
    def crear(cls, email_string: str) -> "Email":
        """
        Factory method para crear un Email validado.
        
        Args:
            email_string: Dirección de email
            
        Returns:
            Email: Instancia validada y normalizada
            
        Raises:
            ValueError: Si el email es inválido
        """
        if not email_string:
            raise ValueError("Email no puede estar vacío")
        
        email_limpio = email_string.strip().lower()
        
        if not cls._PATRON_EMAIL.match(email_limpio):
            raise ValueError(f"Formato de email inválido: {email_string}")
        
        usuario, dominio = email_limpio.split("@")
        
        return cls(
            valor=email_limpio,
            usuario=usuario,
            dominio=dominio
        )
    
    def __str__(self) -> str:
        return self.valor
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self.valor == other.valor
```

### 6.3 src/shared/domain/value_objects/patente.py

```python
"""
Value Object: Patente Vehicular

Representa una patente de vehículo chilena.

Formatos válidos:
- Antiguo: 2 letras + 4 números (ej: AB1234)
- Nuevo: 4 letras + 2 números (ej: ABCD12)
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Patente:
    """
    Value Object para patentes de vehículos chilenos.
    
    Attributes:
        valor: Patente normalizada (uppercase, sin espacios)
        formato: "antiguo" o "nuevo"
        
    Example:
        >>> patente = Patente.crear("abcd-12")
        >>> print(patente.valor)  # "ABCD12"
        >>> print(patente.formato)  # "nuevo"
    """
    
    valor: str
    formato: str
    
    # Patrones para validación
    _PATRON_ANTIGUO = re.compile(r"^[A-Z]{2}\d{4}$")  # AB1234
    _PATRON_NUEVO = re.compile(r"^[A-Z]{4}\d{2}$")    # ABCD12
    
    @classmethod
    def crear(cls, patente_string: str) -> "Patente":
        """
        Factory method para crear una Patente validada.
        
        Args:
            patente_string: Patente en cualquier formato
            
        Returns:
            Patente: Instancia validada y normalizada
            
        Raises:
            ValueError: Si la patente es inválida
        """
        if not patente_string:
            raise ValueError("Patente no puede estar vacía")
        
        # Normalizar: uppercase, sin espacios ni guiones
        patente_limpia = re.sub(r"[\s\-]", "", patente_string.strip().upper())
        
        # Validar formato
        if cls._PATRON_NUEVO.match(patente_limpia):
            formato = "nuevo"
        elif cls._PATRON_ANTIGUO.match(patente_limpia):
            formato = "antiguo"
        else:
            raise ValueError(
                f"Formato de patente inválido: {patente_string}. "
                "Formatos válidos: AB1234 (antiguo) o ABCD12 (nuevo)"
            )
        
        return cls(valor=patente_limpia, formato=formato)
    
    def __str__(self) -> str:
        return self.valor
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Patente):
            return False
        return self.valor == other.valor
```

### 6.4 src/shared/domain/value_objects/__init__.py

```python
"""
Value Objects compartidos del dominio.

Estos objetos son inmutables y se definen por su valor, no por su identidad.
"""

from .rut import RutChileno, es_rut_valido
from .email import Email
from .patente import Patente

__all__ = [
    "RutChileno",
    "es_rut_valido",
    "Email",
    "Patente",
]
```

---

## 7. Shared Domain - Base Entity

### 7.1 src/shared/domain/entities/base_entity.py

```python
"""
Base Entity con campos de auditoría.

Todas las entidades de dominio heredan de esta clase base.

Principios aplicados:
- DRY: Campos comunes definidos una sola vez
- OCP: Extensible mediante herencia
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from abc import ABC


@dataclass
class BaseEntity(ABC):
    """
    Clase base abstracta para todas las entidades del dominio.
    
    Attributes:
        id: Identificador único (None si no está persistido)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
        
    Note:
        Las entidades tienen identidad (id) a diferencia de los Value Objects.
    """
    
    id: Optional[int] = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Hook para validaciones adicionales en subclases"""
        pass
    
    def marcar_actualizado(self) -> None:
        """Actualiza el timestamp de modificación"""
        object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def es_nuevo(self) -> bool:
        """Verifica si la entidad aún no ha sido persistida"""
        return self.id is None
    
    def __eq__(self, other: object) -> bool:
        """Dos entidades son iguales si tienen el mismo ID"""
        if not isinstance(other, BaseEntity):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash basado en el ID para uso en sets/dicts"""
        return hash(self.id) if self.id else hash(id(self))
```

### 7.2 src/shared/domain/entities/__init__.py

```python
"""Entidades base del dominio"""

from .base_entity import BaseEntity

__all__ = ["BaseEntity"]
```

---

## 8. Shared Domain - Excepciones

### 8.1 src/shared/domain/exceptions/domain_exceptions.py

```python
"""
Excepciones de dominio.

Define excepciones específicas del negocio que son independientes
de la infraestructura (HTTP, DB, etc.)

Principios aplicados:
- SRP: Cada excepción representa un error específico
- Separación de capas: Excepciones de dominio != excepciones HTTP
"""


class DomainException(Exception):
    """
    Excepción base para errores de dominio.
    
    Attributes:
        message: Mensaje descriptivo del error
        code: Código de error para identificación
    """
    
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """
    Se lanza cuando no se encuentra una entidad.
    
    Example:
        >>> raise EntityNotFoundException("Buffet", 123)
        EntityNotFoundException: Buffet con ID 123 no encontrado
    """
    
    def __init__(self, entity_name: str, entity_id: int):
        super().__init__(
            message=f"{entity_name} con ID {entity_id} no encontrado",
            code="ENTITY_NOT_FOUND"
        )
        self.entity_name = entity_name
        self.entity_id = entity_id


class DuplicateEntityException(DomainException):
    """
    Se lanza cuando se intenta crear una entidad duplicada.
    
    Example:
        >>> raise DuplicateEntityException("Usuario", "email", "test@test.com")
    """
    
    def __init__(self, entity_name: str, field: str, value: str):
        super().__init__(
            message=f"Ya existe un {entity_name} con {field}: {value}",
            code="DUPLICATE_ENTITY"
        )
        self.entity_name = entity_name
        self.field = field
        self.value = value


class ValidationException(DomainException):
    """
    Se lanza cuando hay errores de validación de negocio.
    
    Example:
        >>> raise ValidationException("El RUT no es válido")
    """
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.field = field


class BusinessRuleException(DomainException):
    """
    Se lanza cuando se viola una regla de negocio.
    
    Example:
        >>> raise BusinessRuleException("No se puede eliminar un buffet con oficios activos")
    """
    
    def __init__(self, message: str):
        super().__init__(message=message, code="BUSINESS_RULE_VIOLATION")


class UnauthorizedException(DomainException):
    """
    Se lanza cuando el usuario no tiene permisos.
    
    Example:
        >>> raise UnauthorizedException("No tiene permisos para ver este oficio")
    """
    
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message=message, code="UNAUTHORIZED")
```

### 8.2 src/shared/domain/exceptions/__init__.py

```python
"""Excepciones de dominio"""

from .domain_exceptions import (
    DomainException,
    EntityNotFoundException,
    DuplicateEntityException,
    ValidationException,
    BusinessRuleException,
    UnauthorizedException,
)

__all__ = [
    "DomainException",
    "EntityNotFoundException",
    "DuplicateEntityException",
    "ValidationException",
    "BusinessRuleException",
    "UnauthorizedException",
]
```

---

## 9. Shared Application - Interfaces

### 9.1 src/shared/application/interfaces/repository.py

```python
"""
Interface base para repositorios.

Define el contrato que deben cumplir todos los repositorios.

Principios aplicados:
- DIP: Las capas superiores dependen de esta abstracción
- ISP: Interface mínima con operaciones CRUD básicas
- LSP: Cualquier implementación debe ser intercambiable
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

# Tipo genérico para entidades
T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Interface genérica para repositorios.
    
    Define operaciones CRUD básicas que todos los repositorios deben implementar.
    
    Type Parameters:
        T: Tipo de entidad que maneja el repositorio
    """
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """
        Obtiene una entidad por su ID.
        
        Args:
            id: ID de la entidad
            
        Returns:
            Optional[T]: La entidad si existe, None si no
        """
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """
        Obtiene una lista paginada de entidades.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            
        Returns:
            List[T]: Lista de entidades
        """
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        Agrega una nueva entidad.
        
        Args:
            entity: Entidad a agregar
            
        Returns:
            T: Entidad con ID asignado
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Actualiza una entidad existente.
        
        Args:
            entity: Entidad con datos actualizados
            
        Returns:
            T: Entidad actualizada
        """
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """
        Elimina una entidad por su ID.
        
        Args:
            id: ID de la entidad a eliminar
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        pass
```

### 9.2 src/shared/application/interfaces/unit_of_work.py

```python
"""
Interface Unit of Work.

Patrón para manejar transacciones de base de datos de forma coherente.

Principios aplicados:
- SRP: Maneja solo la coordinación de transacciones
- DIP: Abstracción para que los use cases no dependan de SQLAlchemy
"""

from abc import ABC, abstractmethod
from typing import Any


class IUnitOfWork(ABC):
    """
    Interface para Unit of Work.
    
    Coordina operaciones de múltiples repositorios en una sola transacción.
    
    Example:
        async with uow:
            await uow.buffets.add(nuevo_buffet)
            await uow.usuarios.add(nuevo_usuario)
            await uow.commit()  # Ambos se guardan o ninguno
    """
    
    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Inicia el contexto de la transacción"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finaliza el contexto (rollback si hay error)"""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Confirma la transacción"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Revierte la transacción"""
        pass
```

### 9.3 src/shared/application/interfaces/__init__.py

```python
"""Interfaces de la capa de aplicación"""

from .repository import IRepository
from .unit_of_work import IUnitOfWork

__all__ = [
    "IRepository",
    "IUnitOfWork",
]
```

---

## 10. Shared Application - Event Bus

### 10.1 src/shared/application/events/event.py

```python
"""
Clases base para eventos de dominio.

Los eventos permiten comunicación desacoplada entre módulos.

Principios aplicados:
- OCP: Nuevos eventos se crean heredando de DomainEvent
- Desacoplamiento: Módulos se comunican via eventos, no importaciones directas
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4


@dataclass
class DomainEvent:
    """
    Clase base para todos los eventos de dominio.
    
    Attributes:
        event_id: ID único del evento
        occurred_at: Timestamp de cuando ocurrió
        
    Example:
        @dataclass
        class OficioCreado(DomainEvent):
            oficio_id: int
            patente: str
    """
    
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def event_type(self) -> str:
        """Nombre del tipo de evento"""
        return self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el evento a diccionario"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "data": {
                k: v for k, v in self.__dict__.items() 
                if k not in ("event_id", "occurred_at")
            }
        }
```

### 10.2 src/shared/application/events/event_bus.py

```python
"""
Interface y implementación del Event Bus.

El Event Bus permite publicar y suscribirse a eventos de forma desacoplada.

Principios aplicados:
- DIP: Los módulos dependen de la interface, no de la implementación
- OCP: Nuevos handlers se agregan sin modificar código existente
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Type
from .event import DomainEvent


class IEventBus(ABC):
    """
    Interface para el Event Bus.
    
    Define operaciones para publicar y suscribirse a eventos.
    """
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publica un evento para que los suscriptores lo procesen.
        
        Args:
            event: Evento a publicar
        """
        pass
    
    @abstractmethod
    def subscribe(
        self, 
        event_type: Type[DomainEvent], 
        handler: Callable
    ) -> None:
        """
        Suscribe un handler a un tipo de evento.
        
        Args:
            event_type: Tipo de evento a escuchar
            handler: Función que procesa el evento
        """
        pass


class InMemoryEventBus(IEventBus):
    """
    Implementación en memoria del Event Bus.
    
    Útil para desarrollo y testing. En producción se puede reemplazar
    por RabbitMQ, Kafka, etc. sin cambiar el código de los módulos.
    
    Example:
        bus = InMemoryEventBus()
        
        # Suscribir handler
        @bus.subscribe(OficioCreado)
        async def handle_oficio_creado(event: OficioCreado):
            print(f"Nuevo oficio: {event.oficio_id}")
        
        # Publicar evento
        await bus.publish(OficioCreado(oficio_id=1, patente="ABCD12"))
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    async def publish(self, event: DomainEvent) -> None:
        """Publica evento a todos los handlers suscritos"""
        event_type = event.event_type
        handlers = self._handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                # Ejecutar handler (soporta sync y async)
                result = handler(event)
                if hasattr(result, '__await__'):
                    await result
            except Exception as e:
                # Log error pero no detener otros handlers
                print(f"Error en handler para {event_type}: {e}")
    
    def subscribe(
        self, 
        event_type: Type[DomainEvent], 
        handler: Callable
    ) -> None:
        """Registra un handler para un tipo de evento"""
        event_name = event_type.__name__
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
    
    def subscribe_decorator(self, event_type: Type[DomainEvent]):
        """
        Decorador para suscribir handlers.
        
        Example:
            @event_bus.subscribe_decorator(OficioCreado)
            async def handle_oficio(event):
                pass
        """
        def decorator(handler: Callable) -> Callable:
            self.subscribe(event_type, handler)
            return handler
        return decorator


# Instancia global del event bus (singleton)
event_bus = InMemoryEventBus()
```

### 10.3 src/shared/application/events/__init__.py

```python
"""Sistema de eventos para comunicación entre módulos"""

from .event import DomainEvent
from .event_bus import IEventBus, InMemoryEventBus, event_bus

__all__ = [
    "DomainEvent",
    "IEventBus",
    "InMemoryEventBus",
    "event_bus",
]
```

---

## 11. Verificación

Después de crear todos los archivos, verifica que la estructura esté correcta:

```powershell
# Desde la raíz del proyecto
tree src /F

# Deberías ver:
# src/
# ├── __init__.py
# ├── core/
# │   ├── __init__.py
# │   └── config.py
# └── shared/
#     ├── __init__.py
#     ├── domain/
#     │   ├── __init__.py
#     │   ├── entities/
#     │   │   ├── __init__.py
#     │   │   └── base_entity.py
#     │   ├── exceptions/
#     │   │   ├── __init__.py
#     │   │   └── domain_exceptions.py
#     │   └── value_objects/
#     │       ├── __init__.py
#     │       ├── rut.py
#     │       ├── email.py
#     │       └── patente.py
#     ├── application/
#     │   ├── __init__.py
#     │   ├── interfaces/
#     │   │   ├── __init__.py
#     │   │   ├── repository.py
#     │   │   └── unit_of_work.py
#     │   └── events/
#     │       ├── __init__.py
#     │       ├── event.py
#     │       └── event_bus.py
#     └── ...
```

---

## 12. Test de Value Objects

Crea un archivo de prueba rápida:

**Archivo:** `tests/unit/shared/test_value_objects.py`

```python
"""Tests para Value Objects"""

import pytest
from src.shared.domain.value_objects import RutChileno, Email, Patente


class TestRutChileno:
    """Tests para RutChileno"""
    
    def test_rut_valido(self):
        """RUT válido se crea correctamente"""
        rut = RutChileno.crear("12345678-5")
        assert rut.numero == 12345678
        assert rut.digito_verificador == "5"
    
    def test_rut_con_puntos(self):
        """RUT con puntos se normaliza"""
        rut = RutChileno.crear("12.345.678-5")
        assert rut.numero == 12345678
    
    def test_rut_invalido_lanza_error(self):
        """RUT con dígito verificador incorrecto lanza error"""
        with pytest.raises(ValueError, match="Dígito verificador inválido"):
            RutChileno.crear("12345678-0")
    
    def test_rut_con_k(self):
        """RUT con dígito K funciona"""
        # 11111111-K es válido
        rut = RutChileno.crear("11111111-K")
        assert rut.digito_verificador == "K"


class TestEmail:
    """Tests para Email"""
    
    def test_email_valido(self):
        """Email válido se crea correctamente"""
        email = Email.crear("test@example.com")
        assert email.valor == "test@example.com"
    
    def test_email_normaliza_a_lowercase(self):
        """Email se normaliza a minúsculas"""
        email = Email.crear("Test@EXAMPLE.COM")
        assert email.valor == "test@example.com"
    
    def test_email_invalido_lanza_error(self):
        """Email inválido lanza error"""
        with pytest.raises(ValueError):
            Email.crear("no-es-email")


class TestPatente:
    """Tests para Patente"""
    
    def test_patente_formato_nuevo(self):
        """Patente formato nuevo se detecta"""
        patente = Patente.crear("ABCD12")
        assert patente.formato == "nuevo"
    
    def test_patente_formato_antiguo(self):
        """Patente formato antiguo se detecta"""
        patente = Patente.crear("AB1234")
        assert patente.formato == "antiguo"
    
    def test_patente_normaliza(self):
        """Patente se normaliza a mayúsculas"""
        patente = Patente.crear("abcd-12")
        assert patente.valor == "ABCD12"
    
    def test_patente_invalida_lanza_error(self):
        """Patente inválida lanza error"""
        with pytest.raises(ValueError):
            Patente.crear("ABC123")  # Formato inválido
```

Para ejecutar:

```powershell
# Instalar dependencias primero
pip install -r requirements.txt

# Ejecutar tests
pytest tests/unit/shared/test_value_objects.py -v
```

---

## 13. Próximo Paso

Una vez que hayas creado todos estos archivos, el siguiente documento será:

**Parte 6: Shared Infrastructure** - Donde crearemos:
- Conexión a base de datos (session.py)
- SQLAlchemy Base
- Middlewares de error y logging
- Dependencies de FastAPI compartidas

¿Listo para continuar? Avísame cuando hayas terminado de crear estos archivos.

