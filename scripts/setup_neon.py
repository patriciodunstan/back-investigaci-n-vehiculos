"""
Script para configurar y verificar conexion a Neon PostgreSQL.

Este script ayuda a:
1. Verificar la conexion a Neon
2. Ejecutar migraciones
3. Crear usuario admin inicial
"""

import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 para Windows (debe ser lo primero)
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Agregar raiz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno desde .env
from dotenv import load_dotenv

load_dotenv(project_root / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from src.core.config import get_settings


def test_connection():
    """Verifica la conexion a la base de datos Neon."""
    print("=" * 60)
    print("VERIFICANDO CONEXION A NEON POSTGRESQL")
    print("=" * 60)

    try:
        settings = get_settings()
        db_url = settings.DATABASE_URL

        # Ocultar password en el log
        safe_url = (
            db_url.split("@")[0].split("//")[0] + "//***:***@" + "@".join(db_url.split("@")[1:])
        )
        print(f"\n[INFO] Conectando a: {safe_url}")

        engine = create_engine(db_url, pool_pre_ping=True)

        with engine.connect() as conn:
            # Test basico
            result = conn.execute(text("SELECT 1"))
            print("[OK] Conexion exitosa a PostgreSQL")

            # Version de PostgreSQL
            version_result = conn.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            print(f"[INFO] Version: {version.split(',')[0]}")

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
                print(f"\n[INFO] Tablas existentes ({len(tables)}):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n[WARN] No hay tablas en la base de datos")
                print("   Ejecuta: alembic upgrade head")

        print("\n" + "=" * 60)
        print("[OK] Conexion verificada correctamente")
        print("=" * 60)
        return True

    except OperationalError as e:
        print(f"\n[ERROR] Error de conexion: {e}")
        print("\n[INFO] Verifica:")
        print("   1. Que DATABASE_URL este configurada en .env")
        print("   2. Que la URL de Neon sea correcta")
        print("   3. Que el proyecto Neon este activo")
        print("   4. Que las credenciales sean correctas")
        return False

    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Funcion principal."""
    # Verificar que DATABASE_URL este configurada
    if not os.getenv("DATABASE_URL"):
        print("[ERROR] DATABASE_URL no esta configurada")
        print("\n[INFO] Configura DATABASE_URL en tu archivo .env")
        print("   Ejemplo:")
        print("   DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require")
        sys.exit(1)

    success = test_connection()

    if success:
        print("\n[PASOS] Proximos pasos:")
        print("   1. Ejecutar migraciones: alembic upgrade head")
        print("   2. Crear usuario admin: python scripts/seed_admin.py")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
