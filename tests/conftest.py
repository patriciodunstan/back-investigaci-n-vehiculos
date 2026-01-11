"""
Configuración y fixtures compartidas para tests.

Este archivo contiene fixtures de pytest que se pueden usar en todos los tests.
"""

import os
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import select, text
from sqlalchemy.exc import ResourceClosedError
from httpx import AsyncClient

# Configurar entorno de test antes de importar
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
# Si DATABASE_URL no está configurado, usar SQLite en memoria
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "test-secret-key-for-testing-only-min-32-chars"
)
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

# Importar modelos para que Base.metadata los conozca
from src.shared.infrastructure.database.models_registry import *  # noqa: F401, F403

from src.shared.infrastructure.database.base import Base
from src.main import app
from src.modules.usuarios.domain.entities import Usuario
from src.modules.usuarios.infrastructure.services import PasswordHasher
from src.modules.buffets.domain.entities import Buffet
from src.shared.domain.enums import RolEnum


# Engine y Session para tests
# Usar DATABASE_URL del entorno si está disponible (CI), sino SQLite en memoria
test_db_url = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

# Convertir DATABASE_URL para async
if test_db_url.startswith("sqlite"):
    # SQLite async: usar aiosqlite
    async_test_db_url = test_db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    test_engine = create_async_engine(
        async_test_db_url,
        echo=False,
        pool_pre_ping=True,
    )
else:
    # PostgreSQL async: usar asyncpg
    # CRÍTICO: Usar NullPool para evitar conflictos de concurrencia con asyncpg
    # NullPool crea una nueva conexión para cada sesión, evitando "another operation is in progress"
    async_test_db_url = test_db_url.replace("postgresql://", "postgresql+asyncpg://")
    test_engine = create_async_engine(
        async_test_db_url,
        echo=False,
        poolclass=NullPool,  # Sin pool: cada sesión obtiene su propia conexión
    )

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Lock para asegurar que las tablas se creen una sola vez
_tables_created_lock = asyncio.Lock()
_tables_created = False


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Fixture de sesión que crea las tablas una vez al inicio de todos los tests.
    """
    global _tables_created
    async with _tables_created_lock:
        if not _tables_created:
            # Crear todas las tablas
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            _tables_created = True
    yield
    # No eliminar tablas aquí, ya que los tests usan rollback para limpiar datos


@pytest.fixture(scope="function", autouse=True)
async def cleanup_test_data():
    """
    Fixture automático que limpia datos de test antes de cada test.

    Con NullPool y rollback, los datos pueden persistir entre tests.
    Este fixture elimina los usuarios y buffets de test conocidos antes de cada test
    usando SQL directo con commit para garantizar la limpieza.
    """
    # Crear una sesión separada para el cleanup (con commit)
    async with TestAsyncSessionLocal() as cleanup_session:
        try:
            # Usar SQL directo para eliminar usuarios de test conocidos
            # Esto es más confiable que usar el ORM
            test_emails = [
                "admin@test.com",
                "investigador@test.com",
                "cliente@test.com",
            ]

            for email in test_emails:
                # Usar SQL directo con parámetros para evitar SQL injection
                await cleanup_session.execute(
                    text("DELETE FROM usuarios WHERE email = :email"), {"email": email}
                )

            # Limpiar buffets de test conocidos
            test_ruts = [
                "12.345.678-5",  # RUT formateado usado en tests (formato normalizado de "12345678-5")
            ]

            for rut in test_ruts:
                await cleanup_session.execute(
                    text("DELETE FROM buffets WHERE rut = :rut"), {"rut": rut}
                )

            await cleanup_session.commit()
        except Exception:
            await cleanup_session.rollback()

    yield

    # Cleanup después del test también (por si acaso)
    async with TestAsyncSessionLocal() as cleanup_session:
        try:
            test_emails = [
                "admin@test.com",
                "investigador@test.com",
                "cliente@test.com",
            ]

            for email in test_emails:
                await cleanup_session.execute(
                    text("DELETE FROM usuarios WHERE email = :email"), {"email": email}
                )

            # Limpiar buffets de test conocidos
            test_ruts = [
                "12.345.678-5",  # RUT formateado usado en tests (formato normalizado de "12345678-5")
            ]

            for rut in test_ruts:
                await cleanup_session.execute(
                    text("DELETE FROM buffets WHERE rut = :rut"), {"rut": rut}
                )

            await cleanup_session.commit()
        except Exception:
            await cleanup_session.rollback()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture para sesión de base de datos de test.

    Crea una sesión para cada test con una transacción explícita.
    Los datos se limpian mediante rollback explícito al finalizar.
    NO hace commit, solo rollback para evitar que los datos persistan entre tests.

    Con NullPool, cada sesión obtiene su propia conexión, por lo que necesitamos
    transacciones explícitas para aislar los datos entre tests.
    """
    # Crear sesión
    async with TestAsyncSessionLocal() as session:
        # Iniciar transacción explícita para aislar cada test
        trans = await session.begin()
        try:
            yield session
        except Exception:
            # Si hay error, hacer rollback de la transacción
            await trans.rollback()
            raise
        finally:
            # Intentar rollback solo si la transacción está activa
            # Si el test hizo commit manual, la transacción ya está cerrada
            try:
                await trans.rollback()
            except ResourceClosedError:
                # La transacción ya fue cerrada (probablemente por commit manual)
                # Esto es válido y no requiere acción
                pass


@pytest.fixture(scope="function")
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture para cliente HTTP asíncrono de FastAPI.

    Override de get_db para usar la sesión de test.
    """

    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from src.shared.infrastructure.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Limpiar override
    app.dependency_overrides.clear()


@pytest.fixture
def password_hasher():
    """Fixture para password hasher."""
    return PasswordHasher()


@pytest.fixture
async def admin_user(db_session: AsyncSession, password_hasher: PasswordHasher) -> Usuario:
    """
    Fixture para usuario admin de prueba.

    Crea un usuario admin en la base de datos de test.
    """
    password_hash = password_hasher.hash("admin123")

    usuario = Usuario.crear(
        email="admin@test.com",
        nombre="Admin Test",
        password_hash=password_hash,
        rol=RolEnum.ADMIN,
    )

    # Guardar en BD
    from src.modules.usuarios.infrastructure.models import UsuarioModel

    model = UsuarioModel(
        email=usuario.email_str,
        nombre=usuario.nombre,
        password_hash=usuario.password_hash,
        rol=usuario.rol,
        activo=usuario.activo,
    )
    db_session.add(model)
    await db_session.flush()
    await db_session.refresh(model)

    object.__setattr__(usuario, "id", model.id)
    object.__setattr__(usuario, "create_at", model.created_at)
    object.__setattr__(usuario, "update_at", model.updated_at)

    return usuario


@pytest.fixture
async def investigador_user(db_session: AsyncSession, password_hasher: PasswordHasher) -> Usuario:
    """
    Fixture para usuario investigador de prueba.
    """
    password_hash = password_hasher.hash("investigador123")

    usuario = Usuario.crear(
        email="investigador@test.com",
        nombre="Investigador Test",
        password_hash=password_hash,
        rol=RolEnum.INVESTIGADOR,
    )

    from src.modules.usuarios.infrastructure.models import UsuarioModel

    model = UsuarioModel(
        email=usuario.email_str,
        nombre=usuario.nombre,
        password_hash=usuario.password_hash,
        rol=usuario.rol,
        activo=usuario.activo,
    )
    db_session.add(model)
    await db_session.flush()
    await db_session.refresh(model)

    object.__setattr__(usuario, "id", model.id)
    object.__setattr__(usuario, "create_at", model.created_at)
    object.__setattr__(usuario, "update_at", model.updated_at)

    return usuario


@pytest.fixture
async def cliente_user(
    db_session: AsyncSession, password_hasher: PasswordHasher, test_buffet
) -> Usuario:
    """
    Fixture para usuario cliente de prueba.
    """
    password_hash = password_hasher.hash("cliente123")

    usuario = Usuario.crear(
        email="cliente@test.com",
        nombre="Cliente Test",
        password_hash=password_hash,
        rol=RolEnum.CLIENTE,
        buffet_id=test_buffet.id,
    )

    from src.modules.usuarios.infrastructure.models import UsuarioModel

    model = UsuarioModel(
        email=usuario.email_str,
        nombre=usuario.nombre,
        password_hash=usuario.password_hash,
        rol=usuario.rol,
        buffet_id=usuario.buffet_id,
        activo=usuario.activo,
    )
    db_session.add(model)
    await db_session.flush()
    await db_session.refresh(model)

    object.__setattr__(usuario, "id", model.id)
    object.__setattr__(usuario, "create_at", model.created_at)
    object.__setattr__(usuario, "update_at", model.updated_at)

    return usuario


@pytest.fixture
async def test_buffet(db_session: AsyncSession) -> Buffet:
    """
    Fixture para buffet de prueba.
    """
    buffet = Buffet.crear(
        nombre="Buffet Test",
        rut="12345678-5",
        email_principal="buffet@test.com",
        telefono="+56912345678",
        contacto_nombre="Contacto Test",
    )

    from src.modules.buffets.infrastructure.models import BuffetModel

    model = BuffetModel(
        nombre=buffet.nombre,
        rut=buffet.rut_str,
        email_principal=buffet.email_str,
        telefono=buffet.telefono,
        contacto_nombre=buffet.contacto_nombre,
        token_tablero=buffet.token_tablero,
        activo=buffet.activo,
    )
    db_session.add(model)
    await db_session.flush()
    await db_session.refresh(model)

    object.__setattr__(buffet, "id", model.id)
    object.__setattr__(buffet, "create_at", model.created_at)
    object.__setattr__(buffet, "update_at", model.updated_at)

    return buffet


@pytest.fixture
async def auth_headers(test_client: AsyncClient, admin_user: Usuario) -> dict:
    """
    Fixture para headers de autenticación.

    Retorna headers con token JWT válido del admin_user.
    """
    response = await test_client.post(
        "/auth/login",
        data={
            "username": admin_user.email_str,
            "password": "admin123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
