# Guía de Desarrollo

Esta guía está dirigida a desarrolladores que trabajarán en el proyecto.

## 🏗️ Arquitectura

### Clean Architecture

El proyecto sigue Clean Architecture con las siguientes capas:

1. **Domain**: Entidades de negocio, Value Objects, Excepciones de dominio
2. **Application**: Use Cases, DTOs, Interfaces
3. **Infrastructure**: Repositorios, Modelos SQLAlchemy, Servicios externos
4. **Presentation**: Routers FastAPI, Schemas Pydantic

### Modular Monolith

Cada módulo es independiente y puede extraerse a microservicio en el futuro:

- `usuarios`: Autenticación y gestión de usuarios
- `buffets`: Gestión de estudios jurídicos clientes
- `oficios`: Gestión de casos de investigación
- `investigaciones`: Timeline y actividades
- `notificaciones`: Sistema de notificaciones

## 📁 Estructura de un Módulo

```
module/
├── domain/
│   ├── entities/          # Entidades de dominio
│   ├── exceptions/        # Excepciones específicas
│   └── value_objects/     # Value Objects (opcional)
├── application/
│   ├── dtos/              # Data Transfer Objects
│   ├── interfaces/        # Interfaces de repositorios
│   └── use_cases/         # Casos de uso
├── infrastructure/
│   ├── models/            # Modelos SQLAlchemy
│   ├── repositories/      # Implementaciones de repositorios
│   └── services/          # Servicios externos (opcional)
└── presentation/
    ├── routers/           # Endpoints FastAPI
    └── schemas/           # Schemas Pydantic
```

## 🔧 Setup de Desarrollo

### 1. Configurar entorno

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar base de datos

```bash
# Iniciar PostgreSQL y Redis
docker-compose up -d

# Ejecutar migraciones
alembic upgrade head

# Crear usuario admin
python scripts/seed_admin.py
```

### 3. Ejecutar en modo desarrollo

```bash
uvicorn src.main:app --reload
```

## 📝 Convenciones de Código

### Nombres

- **Clases**: PascalCase (`Usuario`, `CreateOficioUseCase`)
- **Funciones/Métodos**: snake_case (`get_by_id`, `execute`)
- **Variables**: snake_case (`user_id`, `numero_oficio`)
- **Constantes**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)

### Imports

Orden de imports:

1. Standard library
2. Third-party packages
3. Local application imports

```python
# Standard library
from datetime import datetime
from typing import Optional

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Local
from src.modules.usuarios.domain.entities import Usuario
```

### Docstrings

Usar docstrings estilo Google:

```python
def crear_usuario(email: str, nombre: str) -> Usuario:
    """
    Crea un nuevo usuario en el sistema.

    Args:
        email: Email único del usuario
        nombre: Nombre completo

    Returns:
        Usuario creado con ID asignado

    Raises:
        EmailAlreadyExistsException: Si el email ya existe
    """
    pass
```

## 🧪 Testing

### Estructura de Tests

```
tests/
├── conftest.py           # Fixtures compartidas
├── unit/                 # Tests unitarios
│   └── modules/
└── integration/          # Tests de integración
    └── api/
```

### Escribir Tests

**Tests unitarios**: Mockear dependencias externas

```python
@pytest.mark.asyncio
async def test_create_user(mock_repository):
    use_case = CreateUserUseCase(mock_repository)
    # ...
```

**Tests de integración**: Usar base de datos real

```python
@pytest.mark.asyncio
async def test_create_user_endpoint(test_client, db_session):
    response = test_client.post("/api/v1/users", json={...})
    # ...
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo unitarios
pytest tests/unit/

# Solo integración
pytest tests/integration/

# Con coverage
pytest --cov=src --cov-report=html
```

## 🔄 Flujo de Trabajo

### 1. Crear nueva feature

```bash
# Crear branch
git checkout -b feature/nueva-funcionalidad

# Desarrollar
# ...

# Ejecutar tests
pytest

# Commit
git commit -m "feat: agregar nueva funcionalidad"
```

### 2. Crear migración

```bash
# Generar migración
alembic revision --autogenerate -m "descripcion"

# Revisar migración generada
# Editar si es necesario

# Aplicar migración
alembic upgrade head
```

### 3. Code Review

- Verificar que los tests pasen
- Verificar coverage mínimo (70%)
- Revisar que sigue convenciones
- Verificar que no hay código duplicado

## 🐛 Debugging

### Logs

Los logs se configuran en `src/core/logging_config.py`. En desarrollo, usar nivel `DEBUG`:

```python
# .env
LOG_LEVEL=DEBUG
```

### Base de Datos

Conectar a PostgreSQL:

```bash
psql -h localhost -U postgres -d investigaciones_db
```

### FastAPI Debug Mode

El servidor en modo `--reload` muestra errores detallados en la consola.

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic](https://docs.pydantic.dev/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

