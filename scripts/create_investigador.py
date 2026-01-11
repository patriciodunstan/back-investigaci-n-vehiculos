"""
Script para crear usuario investigador.

Ejecutar para crear un usuario investigador específico.
"""

import sys
import asyncio

sys.path.insert(0, ".")

# Importar registry para que SQLAlchemy detecte todos los modelos
from src.shared.infrastructure.database.models_registry import *  # noqa: F401, F403
from src.shared.infrastructure.database import AsyncSessionLocal
from src.modules.usuarios.infrastructure.repositories import UsuarioRepository
from src.modules.usuarios.application.dtos import RegisterUserDTO
from src.modules.usuarios.application.use_cases import RegisterUserUseCase
from src.modules.usuarios.domain.exceptions import EmailAlreadyExistsException
from src.shared.domain.enums import RolEnum


async def create_investigador():
    """Crea el usuario investigador."""
    print("=" * 60)
    print("CREANDO USUARIO INVESTIGADOR")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            repository = UsuarioRepository(db)
            use_case = RegisterUserUseCase(repository)

            dto = RegisterUserDTO(
                email="jgarrido@detectivesecurity.cl",
                password="jgarrido1234",
                nombre="Juaquin Garrido",
                rol=RolEnum.INVESTIGADOR,
                buffet_id=None,  # Investigadores no tienen buffet_id
            )

            try:
                user = await use_case.execute(dto)
                await db.commit()
                print("\n[OK] Usuario investigador creado exitosamente!")
                print(f"   ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   Nombre: {user.nombre}")
                print(f"   Rol: {user.rol}")
                print("\n" + "=" * 60)
                print("CREDENCIALES DE ACCESO:")
                print("=" * 60)
                print("  Email: jgarrido@detectivesecurity.cl")
                print("  Password: jgarrido1234")
                print("  Rol: INVESTIGADOR")
                print("=" * 60)
            except EmailAlreadyExistsException:
                print("\n[INFO] El usuario ya existe")
                print("  Email: jgarrido@detectivesecurity.cl")
                print("\nSi quieres cambiar la contraseña, puedes:")
                print("  1. Eliminar el usuario desde la BD")
                print("  2. O implementar un endpoint de cambio de contraseña")

        except Exception as e:
            print(f"\n[ERROR] Error al crear investigador: {e}")
            await db.rollback()
            raise


def main():
    """Punto de entrada."""
    asyncio.run(create_investigador())


if __name__ == "__main__":
    main()
