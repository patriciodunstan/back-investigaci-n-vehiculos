# Análisis del Pipeline de CI

## 🔍 Problemas Identificados

### 1. **Migraciones de Alembic innecesarias en tests**

**Problema:**
- El workflow ejecuta `alembic upgrade head` antes de los tests
- Pero los tests crean las tablas desde cero con `Base.metadata.create_all()`
- Esto es redundante y puede causar conflictos

**Solución:**
- No ejecutar migraciones antes de los tests
- Los tests deben crear las tablas desde cero usando `Base.metadata.create_all()`
- Las migraciones solo son necesarias para el deploy, no para los tests

### 2. **Instalación redundante de pytest**

**Problema:**
- `pytest`, `pytest-asyncio`, y `pytest-cov` ya están en `requirements.txt`
- Se vuelven a instalar en el paso "Run tests"
- Esto es redundante pero no debería causar fallos

**Solución:**
- Eliminar la reinstalación de pytest en el paso "Run tests"
- Ya están instalados desde `requirements.txt`

### 3. **Configuración de entorno**

**Problema:**
- No hay variables de entorno configuradas globalmente
- Cada paso tiene que configurar `DATABASE_URL` y `SECRET_KEY` individualmente

**Solución:**
- Mover variables de entorno al nivel del job o usar `env:` a nivel de steps

## 📋 Correcciones Propuestas

### Workflow Corregido

```yaml
name: CI - Tests and Linting

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main

env:
  PYTHON_VERSION: '3.12.7'
  DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
  SECRET_KEY: "test-secret-key-for-ci-only-not-used-in-production"

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip setuptools wheel
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install linting tools
        run: |
          pip install ruff black mypy pylint

      - name: Run Ruff
        run: |
          ruff check src/ --output-format=github || true

      - name: Run Black check
        run: |
          black --check src/ || true

      - name: Run Pylint
        run: |
          pylint src/ --disable=all --enable=error || true
```

## 🔧 Cambios Principales

1. **Eliminado paso "Run migrations"**: Los tests crean las tablas desde cero
2. **Variables de entorno globales**: `DATABASE_URL` y `SECRET_KEY` en `env:` del workflow
3. **Eliminada reinstalación de pytest**: Ya está en requirements.txt
4. **Simplificación**: Menos pasos = menos puntos de fallo

## ⚠️ Notas Importantes

- Los tests en CI usan PostgreSQL (igual que en producción)
- Los tests en local usan SQLite en memoria (más rápido)
- Las migraciones de Alembic se ejecutan solo en deploy (Render)
- Los tests no dependen de las migraciones, crean tablas desde modelos
