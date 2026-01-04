"""
Configuración y fixtures compartidas para tests.

Este archivo contiene fixtures de pytest que se pueden usar en todos los tests.
"""

import os
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Configurar entorno de test antes de importar
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-min-32-chars"
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
from src.shared.domain.value_objects import Email


# Engine y Session para tests
test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Fixture para sesión de base de datos de test.

    Crea todas las tablas antes de cada test y las elimina después.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=test_engine)

    # Crear sesión
    session = TestSessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        # Eliminar todas las tablas después del test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture para cliente HTTP de FastAPI.

    Override de get_db para usar la sesión de test.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from src.shared.infrastructure.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    yield client

    # Limpiar override
    app.dependency_overrides.clear()


@pytest.fixture
def password_hasher():
    """Fixture para password hasher."""
    return PasswordHasher()


@pytest.fixture
def admin_user(db_session: Session, password_hasher: PasswordHasher) -> Usuario:
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
    db_session.flush()
    db_session.refresh(model)

    object.__setattr__(usuario, "id", model.id)
    object.__setattr__(usuario, "create_at", model.created_at)
    object.__setattr__(usuario, "update_at", model.updated_at)

    return usuario


@pytest.fixture
def investigador_user(db_session: Session, password_hasher: PasswordHasher) -> Usuario:
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
    db_session.flush()
    db_session.refresh(model)

    object.__setattr__(usuario, "id", model.id)
    object.__setattr__(usuario, "create_at", model.created_at)
    object.__setattr__(usuario, "update_at", model.updated_at)

    return usuario


@pytest.fixture
def cliente_user(db_session: Session, password_hasher: PasswordHasher, test_buffet) -> Usuario:
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
    db_session.flush()
    db_session.refresh(model)

    object.__setattr__(usuario, "id", model.id)
    object.__setattr__(usuario, "create_at", model.created_at)
    object.__setattr__(usuario, "update_at", model.updated_at)

    return usuario


@pytest.fixture
def test_buffet(db_session: Session) -> Buffet:
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
    db_session.flush()
    db_session.refresh(model)

    object.__setattr__(buffet, "id", model.id)
    object.__setattr__(buffet, "create_at", model.created_at)
    object.__setattr__(buffet, "update_at", model.updated_at)

    return buffet


@pytest.fixture
def auth_headers(test_client: TestClient, admin_user: Usuario) -> dict:
    """
    Fixture para headers de autenticación.

    Retorna headers con token JWT válido del admin_user.
    """
    response = test_client.post(
        "/api/v1/auth/login",
        data={
            "username": admin_user.email_str,
            "password": "admin123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
