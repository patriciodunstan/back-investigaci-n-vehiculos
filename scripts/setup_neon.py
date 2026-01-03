"""
Script para configurar y verificar conexión a Neon PostgreSQL.

Este script ayuda a:
1. Verificar la conexión a Neon
2. Ejecutar migraciones
3. Crear usuario admin inicial
"""

import sys
import os
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from src.core.config import get_settings


def test_connection():
    """Verifica la conexión a la base de datos Neon."""
    print("=" * 60)
    print("VERIFICANDO CONEXIÓN A NEON POSTGRESQL")
    print("=" * 60)

    try:
        settings = get_settings()
        db_url = settings.DATABASE_URL

        # Ocultar password en el log
        safe_url = (
            db_url.split("@")[0].split("//")[0] + "//***:***@" + "@".join(db_url.split("@")[1:])
        )
        print(f"\n📡 Conectando a: {safe_url}")

        engine = create_engine(db_url, pool_pre_ping=True)

        with engine.connect() as conn:
            # Test básico
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a PostgreSQL")

            # Versión de PostgreSQL
            version_result = conn.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            print(f"📦 Versión: {version.split(',')[0]}")

            # Verificar tablas existentes
            tables_result = conn.execute(
                text(
                    """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """
                )
            )
            tables = [row[0] for row in tables_result.fetchall()]

            if tables:
                print(f"\n📋 Tablas existentes ({len(tables)}):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n⚠️  No hay tablas en la base de datos")
                print("   Ejecuta: alembic upgrade head")

        print("\n" + "=" * 60)
        print("✅ Conexión verificada correctamente")
        print("=" * 60)
        return True

    except OperationalError as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\n💡 Verifica:")
        print("   1. Que DATABASE_URL esté configurada en .env")
        print("   2. Que la URL de Neon sea correcta")
        print("   3. Que el proyecto Neon esté activo")
        print("   4. Que las credenciales sean correctas")
        return False

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Función principal."""
    # Verificar que DATABASE_URL esté configurada
    if not os.getenv("DATABASE_URL"):
        print("❌ ERROR: DATABASE_URL no está configurada")
        print("\n💡 Configura DATABASE_URL en tu archivo .env")
        print("   Ejemplo:")
        print("   DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require")
        sys.exit(1)

    success = test_connection()

    if success:
        print("\n📝 Próximos pasos:")
        print("   1. Ejecutar migraciones: alembic upgrade head")
        print("   2. Crear usuario admin: python scripts/seed_admin.py")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
