# 🔍 Por qué Técnicamente Tenemos Código Síncrono en las Llamadas a Base de Datos

## 📋 Resumen Ejecutivo

El proyecto está usando **SQLAlchemy síncrono** (`create_engine`, `Session`) en lugar de **SQLAlchemy asíncrono** (`create_async_engine`, `AsyncSession`), aunque los métodos de los repositorios están marcados como `async`. Esto crea un patrón híbrido que funciona pero **no es óptimo** para aplicaciones FastAPI de alto rendimiento.

---

## 🔧 Análisis Técnico Detallado

### 1. Configuración Actual (Síncrona)

#### `src/shared/infrastructure/database/session.py`

```python
# ❌ SQLAlchemy SÍNCRONO
from sqlalchemy import create_engine  # <-- Síncrono
from sqlalchemy.orm import Session     # <-- Síncrono

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    # ... configuración
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:  # <-- Retorna Session síncrona
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

**Características:**
- ✅ `create_engine`: Motor síncrono que bloquea el hilo mientras espera respuesta de PostgreSQL
- ✅ `Session`: Sesión síncrona que ejecuta queries de forma bloqueante
- ✅ `get_db()`: Generator síncrono que retorna `Session`, no `AsyncSession`

---

### 2. Uso en Repositorios (Híbrido - Inconsistente)

#### Ejemplo: `src/modules/oficios/infrastructure/repositories/oficio_repository.py`

```python
from sqlalchemy.orm import Session  # <-- Síncrono

class OficioRepository(IOficioRepository):
    def __init__(self, session: Session):  # <-- Recibe Session síncrona
        self._session = session

    # ⚠️ Método marcado como async pero usa código síncrono
    async def get_by_numero(self, numero_oficio: str) -> Optional[OficioModel]:
        stmt = select(OficioModel).where(OficioModel.numero_oficio == numero_oficio.upper())
        result = self._session.execute(stmt)  # <-- SÍNCRONO, NO usa await
        return result.scalar_one_or_none()

    # ⚠️ Método marcado como async pero usa código síncrono
    async def add(self, oficio: OficioModel) -> OficioModel:
        self._session.add(oficio)      # <-- SÍNCRONO
        self._session.flush()          # <-- SÍNCRONO, bloquea el hilo
        return oficio
```

**Problemas identificados:**
- ❌ Los métodos están marcados como `async` pero **no usan `await`**
- ❌ `self._session.execute(stmt)` es **síncrono y bloqueante**
- ❌ `self._session.flush()` es **síncrono y bloqueante**
- ⚠️ FastAPI ejecutará estas funciones en un **thread pool** cuando detecte código síncrono en funciones `async`

---

### 3. Cómo FastAPI Maneja Esto

Cuando FastAPI encuentra una función `async` que llama a código síncrono bloqueante:

```python
# En un endpoint FastAPI
@router.get("/oficios/{oficio_id}")
async def get_oficio(  # <-- async
    oficio_id: int,
    db: Session = Depends(get_db)  # <-- Session síncrona
):
    repository = OficioRepository(db)
    # ⚠️ Esto se ejecutará en un thread pool porque:
    # 1. La función es async
    # 2. Pero get_by_id() llama a código síncrono (self._session.execute)
    oficio = await repository.get_by_numero("123")  # <-- await aquí
    return oficio
```

**Qué pasa internamente:**

1. FastAPI detecta que `repository.get_by_numero()` es `async`
2. Pero cuando ejecuta `self._session.execute(stmt)`, es código **síncrono bloqueante**
3. FastAPI automáticamente ejecuta esto en un **thread pool** para no bloquear el event loop
4. El hilo se bloquea esperando respuesta de PostgreSQL
5. El event loop puede manejar otros requests mientras tanto (parcialmente beneficioso)

**Problema:**
- 🐌 Más lento que usar SQLAlchemy asíncrono nativo
- 💾 Consume más recursos (threads adicionales)
- ⚠️ No aprovecha completamente el modelo asíncrono de FastAPI

---

## 🎯 Razones Técnicas por las que Está Implementado Así

### Razón 1: Familiaridad y Simplicidad Inicial

**Ventajas:**
- ✅ SQLAlchemy síncrono es más maduro y documentado
- ✅ Más ejemplos disponibles en la comunidad
- ✅ Más fácil de depurar en desarrollo
- ✅ Herramientas como `alembic` funcionan mejor con síncrono (aunque soportan async)

**Desventajas:**
- ❌ No aprovecha el modelo asíncrono de FastAPI
- ❌ Menor rendimiento en alta concurrencia

---

### Razón 2: Legacy o Migración Gradual

Es posible que el proyecto haya comenzado con código síncrono y luego se agregaron las funciones `async` para mantener compatibilidad con la interfaz, pero sin migrar completamente la infraestructura.

**Estado actual:**
- ✅ Interfaces (`IOficioRepository`) definen métodos `async`
- ❌ Implementaciones usan SQLAlchemy síncrono
- ⚠️ Mezcla inconsistente

---

### Razón 3: Compatibilidad con Alembic

Aunque Alembic soporta async desde la versión 1.10+, la configuración por defecto y muchos ejemplos usan código síncrono:

```python
# alembic/env.py típico (síncrono)
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()
```

**Migrar a async requiere cambios:**
```python
# alembic/env.py async
from sqlalchemy.ext.asyncio import create_async_engine

async def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    # Convertir postgresql:// a postgresql+asyncpg://
    async_engine = create_async_engine(url)
    # ... más cambios
```

---

### Razón 4: No es Crítico para el Rendimiento Actual

Si el proyecto:
- ✅ No maneja miles de requests concurrentes
- ✅ Las queries son relativamente rápidas (< 100ms)
- ✅ El pool de conexiones está bien configurado

**Entonces:**
- El código síncrono puede ser aceptable temporalmente
- FastAPI + thread pool es suficientemente rápido para muchos casos de uso
- La migración a async puede ser una optimización futura

---

## 📊 Comparación: Síncrono vs Asíncrono

### Arquitectura Síncrona (Actual)

```
Request → FastAPI → Endpoint async → Repository async → Session.execute() [BLOQUEA HILO]
                                                                  ↓
                                                          Thread Pool
                                                                  ↓
                                                          PostgreSQL
```

**Características:**
- 🔴 Bloquea hilos del thread pool
- 🟡 FastAPI puede manejar otros requests (limitado por threads)
- 🟡 Pool de conexiones: 5-10 conexiones típico

**Rendimiento:**
- ~100-200 requests/segundo (depende de queries)
- Latencia: ~50-200ms (espera de BD)

---

### Arquitectura Asíncrona (Óptima)

```
Request → FastAPI → Endpoint async → Repository async → await session.execute() [NO BLOQUEA]
                                                                  ↓
                                                          AsyncPG / async driver
                                                                  ↓
                                                          PostgreSQL
```

**Características:**
- 🟢 No bloquea hilos (usa event loop)
- 🟢 FastAPI puede manejar miles de requests concurrentes
- 🟢 Pool de conexiones: 20-50 conexiones típico

**Rendimiento:**
- ~500-1000+ requests/segundo (depende de queries)
- Latencia: ~20-100ms (espera de BD pero sin bloqueo)

---

## 🔄 Qué Necesitarías para Migrar a Asíncrono

### Paso 1: Cambiar el Engine

```python
# ❌ Actual (síncrono)
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)

# ✅ Nuevo (asíncrono)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=20,
    max_overflow=10,
)
```

### Paso 2: Cambiar la Session

```python
# ❌ Actual
from sqlalchemy.orm import sessionmaker, Session
SessionLocal = sessionmaker(bind=engine)

# ✅ Nuevo
from sqlalchemy.ext.asyncio import async_sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Paso 3: Cambiar `get_db()`

```python
# ❌ Actual
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    finally:
        db.close()

# ✅ Nuevo
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Paso 4: Actualizar Repositorios

```python
# ❌ Actual
async def get_by_id(self, id: int):
    result = self._session.execute(stmt)  # Síncrono
    return result.scalar_one_or_none()

# ✅ Nuevo
async def get_by_id(self, id: int):
    result = await self._session.execute(stmt)  # Asíncrono
    return result.scalar_one_or_none()
```

### Paso 5: Actualizar Dependencias

```bash
# Agregar driver asíncrono
pip install asyncpg  # Para PostgreSQL
# o
pip install aiomysql  # Para MySQL
```

### Paso 6: Actualizar Alembic

```python
# alembic/env.py
from sqlalchemy.ext.asyncio import create_async_engine

async def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    url = url.replace("postgresql://", "postgresql+asyncpg://")
    async_engine = create_async_engine(url)
    # ... resto de la configuración
```

---

## ✅ Recomendaciones

### Opción 1: Mantener Síncrono (Si funciona bien)

**Haz:**
- ✅ Convierte métodos `async` a `def` normales (más honesto)
- ✅ Asegúrate de que el pool de conexiones esté bien configurado
- ✅ Usa `@router.get()` sin `async` si el endpoint es completamente síncrono

```python
# Más honesto: síncrono explícito
@router.get("/oficios/{id}")  # Sin async
def get_oficio(id: int, db: Session = Depends(get_db)):
    repository = OficioRepository(db)
    return repository.get_by_id(id)  # Sin await
```

**Ventajas:**
- 🟢 Más simple y directo
- 🟢 No hay confusión sobre qué es async y qué no
- 🟢 FastAPI manejará en thread pool automáticamente

---

### Opción 2: Migrar a Asíncrono (Para mejor rendimiento)

**Haz:**
- ✅ Migra todo el stack a async (engine, session, repositorios)
- ✅ Usa `asyncpg` como driver
- ✅ Actualiza Alembic para async
- ✅ Actualiza todos los tests

**Ventajas:**
- 🟢 Mejor rendimiento en alta concurrencia
- 🟢 Aprovecha completamente FastAPI asíncrono
- 🟢 Escalabilidad mejorada

**Desventajas:**
- 🔴 Requiere cambios significativos en todo el código
- 🔴 Más complejidad en tests y migraciones
- 🔴 Curva de aprendizaje

---

### Opción 3: Híbrido (No recomendado)

**No hagas:**
- ❌ Mantener la mezcla actual (`async` con código síncrono)
- ❌ Esto crea confusión y no aporta beneficios reales

---

## 🎓 Conclusión

**Por qué técnicamente tienen código síncrono:**

1. **SQLAlchemy síncrono es más simple** para comenzar
2. **FastAPI maneja el bloqueo** automáticamente en thread pool
3. **No era crítico** para el rendimiento inicial
4. **Compatibilidad con Alembic** y herramientas existentes

**Estado actual:**
- ⚠️ Mezcla inconsistente: métodos `async` con código síncrono
- ⚠️ Funciona pero no es óptimo
- ✅ FastAPI lo maneja pero con overhead de threads

**Recomendación:**
- 🎯 **Corto plazo**: Mantener síncrono pero hacerlo explícito (quitar `async` donde no se usa)
- 🎯 **Mediano plazo**: Evaluar si necesitas async basado en métricas de rendimiento
- 🎯 **Largo plazo**: Migrar completamente a async si el proyecto escala

---

## 📚 Referencias

- [FastAPI - Async SQL Databases](https://fastapi.tiangolo.com/advanced/async-sql-databases/)
- [SQLAlchemy AsyncIO Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Async Support](https://alembic.sqlalchemy.org/en/latest/branches.html#working-with-async-engines)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/current/)

