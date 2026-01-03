# Guía de Testing

Esta guía explica cómo escribir y ejecutar tests en el proyecto.

## 🎯 Estrategia de Testing

### Pirámide de Tests

1. **Tests Unitarios** (base): Tests rápidos, aislados, con mocks
2. **Tests de Integración** (medio): Tests con base de datos real
3. **Tests E2E** (cima): Tests completos del flujo (futuro)

### Coverage Objetivo

- **Mínimo**: 70%
- **Objetivo**: 80%+
- **Crítico**: Domain y Application layers deben tener >90%

## 📁 Estructura

```
tests/
├── conftest.py              # Fixtures compartidas
├── fixtures/                # Datos de prueba
├── utils/                   # Utilidades de testing
├── unit/                    # Tests unitarios
│   ├── modules/
│   │   ├── usuarios/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   └── infrastructure/
│   │   └── ...
│   └── shared/
└── integration/             # Tests de integración
    └── api/
```

## 🧪 Fixtures

### Fixtures Disponibles

En `tests/conftest.py`:

- `db_session`: Sesión de base de datos para tests
- `test_client`: Cliente HTTP de FastAPI
- `password_hasher`: Instancia de PasswordHasher
- `admin_user`: Usuario admin de prueba
- `investigador_user`: Usuario investigador de prueba
- `cliente_user`: Usuario cliente de prueba
- `test_buffet`: Buffet de prueba
- `auth_headers`: Headers con token JWT válido

### Usar Fixtures

```python
def test_example(db_session, test_client, admin_user):
    # db_session: Sesión de BD
    # test_client: Cliente HTTP
    # admin_user: Usuario admin creado
    pass
```

## ✍️ Escribir Tests Unitarios

### Estructura

```python
import pytest
from unittest.mock import AsyncMock

class TestCreateUserUseCase:
    """Tests para CreateUserUseCase"""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_repository):
        return CreateUserUseCase(mock_repository)

    @pytest.mark.asyncio
    async def test_create_user_exitoso(self, use_case, mock_repository):
        # Arrange
        dto = CreateUserDTO(...)
        mock_repository.exists_by_email.return_value = False

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.id is not None
        mock_repository.add.assert_called_once()
```

### Mocking

**Repositorios**:

```python
mock_repo = AsyncMock()
mock_repo.get_by_id.return_value = usuario
mock_repo.add.return_value = usuario_creado
```

**Servicios externos**:

```python
from unittest.mock import patch

with patch("module.service.external_api") as mock_api:
    mock_api.call.return_value = {"result": "ok"}
    # ...
```

## 🔗 Escribir Tests de Integración

### Estructura

```python
import pytest
from fastapi import status

class TestUserEndpoints:
    """Tests para endpoints de usuarios"""

    @pytest.mark.asyncio
    async def test_create_user(self, test_client, auth_headers):
        response = test_client.post(
            "/api/v1/users",
            headers=auth_headers,
            json={
                "email": "test@test.com",
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "test@test.com"
```

### Base de Datos en Tests

- Cada test obtiene una sesión limpia (`db_session`)
- Las tablas se crean antes de cada test
- Las tablas se eliminan después de cada test
- Usa SQLite en memoria para velocidad

## 🏃 Ejecutar Tests

### Todos los tests

```bash
# Windows
.\scripts\run_tests.ps1

# Linux/Mac
./scripts/run_tests.sh

# O directamente
pytest
```

### Tests específicos

```bash
# Por archivo
pytest tests/unit/modules/usuarios/application/test_register_user.py

# Por función
pytest tests/unit/modules/usuarios/application/test_register_user.py::TestRegisterUserUseCase::test_register_user_exitoso

# Por marcador
pytest -m unit
pytest -m integration
```

### Con coverage

```bash
pytest --cov=src --cov-report=html
```

Reporte HTML en `htmlcov/index.html`.

## ✅ Mejores Prácticas

### 1. Nombres descriptivos

```python
# ❌ Mal
def test_user():
    pass

# ✅ Bien
def test_create_user_with_valid_email_returns_user_with_id():
    pass
```

### 2. Arrange-Act-Assert

```python
def test_example():
    # Arrange: Preparar datos
    dto = CreateUserDTO(...)
    
    # Act: Ejecutar acción
    result = use_case.execute(dto)
    
    # Assert: Verificar resultado
    assert result.id is not None
```

### 3. Un test, una aserción (cuando sea posible)

```python
# ✅ Bien
def test_user_has_id(user):
    assert user.id is not None

def test_user_has_email(user):
    assert user.email is not None
```

### 4. Tests independientes

Cada test debe poder ejecutarse solo sin depender de otros.

### 5. Mockear dependencias externas

En tests unitarios, siempre mockear:
- Repositorios
- Servicios externos (APIs, email, etc.)
- Base de datos

### 6. Usar fixtures para datos comunes

```python
@pytest.fixture
def sample_user():
    return Usuario.crear(...)

def test_one(sample_user):
    # Usa sample_user

def test_two(sample_user):
    # Usa sample_user
```

## 🐛 Debugging Tests

### Ver output completo

```bash
pytest -v -s
```

### Ejecutar solo un test

```bash
pytest tests/unit/test_file.py::test_function -v
```

### PDB debugger

```python
def test_example():
    result = use_case.execute(dto)
    import pdb; pdb.set_trace()  # Breakpoint
    assert result.id is not None
```

## 📊 Coverage

### Verificar coverage

```bash
pytest --cov=src --cov-report=term-missing
```

### Excluir archivos

En `pytest.ini`:

```ini
[coverage:run]
omit =
    */tests/*
    */migrations/*
    */__init__.py
```

### Threshold mínimo

El proyecto requiere mínimo 70% de coverage. Si baja, los tests fallan.

## 🔍 Troubleshooting

### Import errors

Asegurarse de que `pytest.ini` tiene:

```ini
[pytest]
pythonpath = .
```

### Database errors

Verificar que `conftest.py` crea las tablas correctamente:

```python
Base.metadata.create_all(bind=test_engine)
```

### Async tests

Usar `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
```

