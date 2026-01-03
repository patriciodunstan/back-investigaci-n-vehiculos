"""
Script para crear usuario admin inicial.

Ejecutar una sola vez para crear el primer usuario admin.
"""

import sys
import asyncio

sys.path.insert(0, ".")

# Importar registry para que SQLAlchemy detecte todos los modelos
from src.shared.infrastructure.database.models_registry import *  # noqa: F401, F403
from src.shared.infrastructure.database import SessionLocal
from src.modules.usuarios.infrastructure.repositories import UsuarioRepository
from src.modules.usuarios.application.dtos import RegisterUserDTO
from src.modules.usuarios.application.use_cases import RegisterUserUseCase
from src.modules.usuarios.domain.exceptions import EmailAlreadyExistsException
from src.shared.domain.enums import RolEnum


async def create_admin():
    """Crea el usuario admin inicial."""
    print("=" * 50)
    print("CREANDO USUARIO ADMIN INICIAL")
    print("=" * 50)

    db = SessionLocal()
    try:
        repository = UsuarioRepository(db)
        use_case = RegisterUserUseCase(repository)

        dto = RegisterUserDTO(
            email="admin@sistema.com",
            password="admin123",
            nombre="Administrador Sistema",
            rol=RolEnum.ADMIN,
            buffet_id=None,
        )

        try:
            user = await use_case.execute(dto)
            db.commit()
            print("\n[OK] Usuario admin creado exitosamente!")
            print(f"   Email: {user.email}")
            print(f"   Nombre: {user.nombre}")
            print(f"   Rol: {user.rol}")
            print(f"   ID: {user.id}")
        except EmailAlreadyExistsException:
            print("\n[INFO] El usuario admin ya existe")

        print("\n" + "=" * 50)
        print("Credenciales de acceso:")
        print("  Email: admin@sistema.com")
        print("  Password: admin123")
        print("=" * 50)

    except Exception as e:
        print(f"\n[ERROR] Error al crear admin: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Punto de entrada."""
    asyncio.run(create_admin())


if __name__ == "__main__":
    main()
