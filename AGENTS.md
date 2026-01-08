# AGENTS.md - Guía para Agentes de IA

Este documento proporciona instrucciones para agentes de IA (GitHub Copilot, Cursor, Claude, etc.) que trabajen en este proyecto.

## 📁 Estructura del Proyecto

```
src/
├── core/                          # Configuración central (settings, logging)
├── shared/                        # Componentes compartidos entre módulos
│   ├── domain/                    # Entidades base, Value Objects, Enums
│   ├── application/               # Interfaces compartidas, Event Bus
│   ├── infrastructure/            # Database, UoW, APIs externas
│   └── presentation/              # Middlewares, schemas compartidos
└── modules/                       # Módulos de negocio independientes
    ├── usuarios/                  # Autenticación y gestión de usuarios
    ├── buffets/                   # Gestión de estudios jurídicos
    ├── oficios/                   # Gestión de oficios de investigación
    ├── investigaciones/           # Timeline y actividades
    └── notificaciones/            # Sistema de notificaciones
```

### Estructura de Cada Módulo

Cada módulo sigue **Clean Architecture** con 4 capas:

```
modulo/
├── domain/              # Entidades, Value Objects, Excepciones de dominio
├── application/         # Use Cases, DTOs, Interfaces (puertos)
│   ├── dtos/           # Data Transfer Objects (dataclasses inmutables)
│   ├── interfaces/     # Contratos abstractos (ABC)
│   └── use_cases/      # Casos de uso del negocio
├── infrastructure/      # Implementaciones concretas (adaptadores)
│   ├── models/         # Modelos SQLAlchemy
│   ├── repositories/   # Implementación de repositorios
│   └── services/       # Servicios externos
└── presentation/        # API REST
    ├── routers/        # Endpoints FastAPI
    └── schemas/        # Schemas Pydantic para request/response
```

---

## 🎯 Principios de Arquitectura

### Clean Architecture
- **Domain**: Entidades puras sin dependencias externas
- **Application**: Casos de uso que orquestan la lógica de negocio
- **Infrastructure**: Implementaciones concretas (DB, APIs, etc.)
- **Presentation**: Capa HTTP (FastAPI routers)

### Flujo de Dependencias
```
Presentation → Application → Domain
      ↓              ↓
Infrastructure ←────┘
```
Las capas internas NO conocen a las externas. Application define interfaces que Infrastructure implementa.

### SOLID Principles
- **S**ingle Responsibility: Cada clase tiene una sola razón para cambiar
- **O**pen/Closed: Abierto para extensión, cerrado para modificación
- **L**iskov Substitution: Los subtipos deben ser sustituibles
- **I**nterface Segregation: Interfaces pequeñas y específicas
- **D**ependency Inversion: Depender de abstracciones, no de implementaciones

---

## 📝 Convenciones de Código

### Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Archivos | snake_case | `oficio_repository.py` |
| Clases | PascalCase | `OficioRepository` |
| Funciones/métodos | snake_case | `get_by_id()` |
| Constantes | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Variables | snake_case | `oficio_id` |
| Enums | PascalCase + UPPER values | `EstadoOficioEnum.PENDIENTE` |

### Sufijos de Clases

| Tipo | Sufijo | Ejemplo |
|------|--------|---------|
| Modelos SQLAlchemy | `Model` | `OficioModel` |
| DTOs | `DTO` | `OficioDTO`, `OficioResponseDTO` |
| Schemas Pydantic | `Request`/`Response` | `CreateOficioRequest` |
| Casos de uso | `UseCase` | `CreateOficioUseCase` |
| Repositorios | `Repository` | `OficioRepository` |
| Interfaces | `I` prefix | `IOficioRepository` |
| Excepciones | `Exception`/`Error` | `OficioNotFoundException` |
| Enums | `Enum` | `EstadoOficioEnum` |

### Imports
```python
# Orden de imports:
# 1. Standard library
from datetime import datetime
from typing import Optional, List

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. Local - shared
from src.shared.domain.enums import EstadoOficioEnum

# 4. Local - mismo módulo
from src.modules.oficios.application.dtos import OficioDTO
```

---

## 🔧 Patrones de Implementación

### 1. Crear un Nuevo Modelo (SQLAlchemy)

```python
# src/modules/{modulo}/infrastructure/models/{nombre}_model.py
"""
Modelo SQLAlchemy para {Nombre}.

Principios aplicados:
- SRP: Solo define la estructura de la tabla
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import MiEnum


class NombreModel(Base):
    """Modelo de base de datos para {nombre}."""

    __tablename__ = "nombres"

    # Columnas con comentarios
    campo = Column(String(255), nullable=False, comment="Descripción del campo")
    
    # FKs con índices
    otro_id = Column(
        Integer,
        ForeignKey("otros.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    otro = relationship("OtroModel", back_populates="nombres")
```

**IMPORTANTE**: Registrar el modelo en `src/shared/infrastructure/database/models_registry.py`

### 2. Crear un Nuevo DTO

```python
# src/modules/{modulo}/application/dtos/{nombre}_dto.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)  # Inmutable
class NombreDTO:
    """DTO para crear/actualizar {nombre}."""
    campo_requerido: str
    campo_opcional: Optional[str] = None


@dataclass(frozen=True)
class NombreResponseDTO:
    """DTO para respuestas de {nombre}."""
    id: int
    campo_requerido: str
    campo_opcional: Optional[str]
    created_at: datetime
```

### 3. Crear un Caso de Uso

```python
# src/modules/{modulo}/application/use_cases/{accion}_{nombre}.py
"""
Caso de uso para {acción} {nombre}.
"""

from src.modules.{modulo}.application.interfaces import IRepository
from src.modules.{modulo}.application.dtos import NombreDTO, NombreResponseDTO
from src.modules.{modulo}.domain.exceptions import NotFoundException


class AccionNombreUseCase:
    """
    Caso de uso para {descripción}.
    
    Responsabilidades:
    - Validar reglas de negocio
    - Orquestar la operación
    - Retornar DTO de respuesta
    """

    def __init__(self, repository: IRepository):
        self._repository = repository

    async def execute(self, dto: NombreDTO) -> NombreResponseDTO:
        """
        Ejecuta el caso de uso.
        
        Args:
            dto: Datos de entrada
        
        Returns:
            NombreResponseDTO con los datos creados
        
        Raises:
            NotFoundException: Si no existe el recurso
        """
        # 1. Validaciones de negocio
        # 2. Crear/modificar entidad
        # 3. Persistir
        # 4. Retornar DTO
        pass
```

### 4. Crear un Endpoint (Router)

```python
# src/modules/{modulo}/presentation/routers/{nombre}_router.py
"""
Router para {nombre}.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db
from src.modules.{modulo}.presentation.schemas import (
    CreateNombreRequest,
    NombreResponse,
)
from src.modules.{modulo}.application.use_cases import AccionNombreUseCase
from src.modules.{modulo}.infrastructure.repositories import NombreRepository


router = APIRouter(prefix="/nombres", tags=["Nombres"])


@router.post(
    "/",
    response_model=NombreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nombre",
    description="Descripción detallada del endpoint.",
)
async def create_nombre(
    request: CreateNombreRequest,
    db: AsyncSession = Depends(get_db),
):
    """Crea un nuevo nombre."""
    repository = NombreRepository(db)
    use_case = AccionNombreUseCase(repository)
    
    dto = NombreDTO(campo=request.campo)
    result = await use_case.execute(dto)
    
    return NombreResponse.model_validate(result.__dict__)
```

### 5. Crear un Enum Compartido

```python
# src/shared/domain/enums.py
class MiNuevoEnum(str, Enum):
    """
    Descripción del enum.
    
    Valores:
    - VALOR_1: Descripción
    - VALOR_2: Descripción
    """
    VALOR_1 = "valor_1"
    VALOR_2 = "valor_2"
```

### 6. Crear una Migración Alembic

```bash
# Generar migración automática
alembic revision --autogenerate -m "descripcion_cambio"

# O crear manualmente en alembic/versions/
```

Ejemplo de migración manual:
```python
"""descripcion_cambio

Revision ID: abc123
Revises: xyz789
Create Date: 2026-01-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'abc123'
down_revision = 'xyz789'


def upgrade() -> None:
    # Crear enum con manejo de existencia
    connection = op.get_bind()
    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE mi_enum AS ENUM ('VALOR_1', 'VALOR_2');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))
    
    # Agregar columna
    op.add_column('tabla', sa.Column(
        'columna',
        postgresql.ENUM('VALOR_1', 'VALOR_2', name='mi_enum', create_type=False),
        nullable=False,
        server_default='VALOR_1'
    ))


def downgrade() -> None:
    op.drop_column('tabla', 'columna')
```

---

## 🔌 Integración de APIs Externas

Las APIs externas se ubican en `src/shared/infrastructure/external_apis/`:

```
external_apis/
└── nombre_api/
    ├── __init__.py      # Exportaciones públicas
    ├── client.py        # Cliente HTTP con singleton
    ├── schemas.py       # Modelos Pydantic de respuesta
    └── exceptions.py    # Excepciones específicas
```

### Patrón de Cliente

```python
# client.py
import httpx
from src.core.config import get_settings

_client_instance: Optional["MiAPIClient"] = None


class MiAPIClient:
    """Cliente para Mi API."""
    
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
    
    async def get_resource(self, id: str) -> ResourceSchema:
        """Obtiene un recurso."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self._base_url}/resource/{id}",
                headers={"Authorization": f"Bearer {self._api_key}"}
            )
            response.raise_for_status()
            return ResourceSchema.model_validate(response.json())


def get_mi_api_client() -> MiAPIClient:
    """Singleton del cliente."""
    global _client_instance
    if _client_instance is None:
        settings = get_settings()
        _client_instance = MiAPIClient(
            api_key=settings.MI_API_KEY,
            base_url=settings.MI_API_URL,
        )
    return _client_instance
```

---

## ✅ Checklist para Nuevas Funcionalidades

### Agregar un nuevo campo a un modelo existente:

1. [ ] Modificar el modelo en `infrastructure/models/`
2. [ ] Actualizar DTOs en `application/dtos/`
3. [ ] Actualizar schemas Pydantic en `presentation/schemas/`
4. [ ] Actualizar el `__init__.py` si hay nuevas exportaciones
5. [ ] Crear migración Alembic
6. [ ] Actualizar casos de uso que usen el modelo
7. [ ] Verificar compilación: `python -c "from src.main import app"`
8. [ ] Ejecutar migración: `alembic upgrade head`

### Agregar un nuevo endpoint:

1. [ ] Crear/actualizar schema en `presentation/schemas/`
2. [ ] Crear DTO en `application/dtos/`
3. [ ] Crear caso de uso en `application/use_cases/`
4. [ ] Actualizar interfaz del repositorio si es necesario
5. [ ] Implementar método en repositorio
6. [ ] Crear endpoint en `presentation/routers/`
7. [ ] Exportar en `__init__.py` correspondientes
8. [ ] Verificar compilación

### Agregar un nuevo módulo:

1. [ ] Crear estructura de carpetas completa
2. [ ] Crear `__init__.py` en cada nivel
3. [ ] Registrar router en `src/main.py`
4. [ ] Registrar modelos en `models_registry.py`
5. [ ] Crear migración para nuevas tablas

---

## 🚫 Anti-patrones a Evitar

1. **NO** importar modelos de infraestructura en el dominio
2. **NO** usar SQLAlchemy directamente en casos de uso (usar repositorio)
3. **NO** retornar modelos SQLAlchemy desde casos de uso (usar DTOs)
4. **NO** poner lógica de negocio en routers (moverla a use cases)
5. **NO** crear dependencias circulares entre módulos
6. **NO** hardcodear configuraciones (usar `get_settings()`)
7. **NO** olvidar el `__init__.py` con exportaciones
8. **NO** crear migraciones sin probar localmente primero

---

## 🔍 Comandos Útiles

```bash
# Verificar compilación
python -c "from src.main import app; print('OK')"

# Ejecutar servidor de desarrollo
uvicorn src.main:app --reload

# Ver historial de migraciones
alembic history

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ejecutar tests
pytest

# Ejecutar tests con cobertura
pytest --cov=src --cov-report=html
```

---

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Clean Architecture - Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
