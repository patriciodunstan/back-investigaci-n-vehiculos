"""Script para verificar las tablas creadas en PostgreSQL."""

import sys

sys.path.insert(0, ".")

from src.shared.infrastructure.database import engine
from sqlalchemy import text


def verify_tables():
    """Lista todas las tablas en el schema public."""
    print("=" * 50)
    print("VERIFICACION DE TABLAS EN POSTGRESQL")
    print("=" * 50)

    try:
        with engine.connect() as conn:
            # Obtener tablas
            result = conn.execute(
                text(
                    """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
                )
            )
            tables = result.fetchall()

            print(f"\n[OK] {len(tables)} tablas encontradas:\n")
            for table in tables:
                print(f"   - {table[0]}")

            # Verificar las tablas esperadas
            expected = {
                "alembic_version",
                "buffets",
                "usuarios",
                "oficios",
                "vehiculos",
                "propietarios",
                "direcciones",
                "investigaciones",
                "avistamientos",
                "adjuntos",
                "notificaciones",
            }
            found = {t[0] for t in tables}

            missing = expected - found
            if missing:
                print(f"\n[WARN] Tablas faltantes: {missing}")
            else:
                print("\n[OK] Todas las tablas esperadas estan presentes!")

            print("\n" + "=" * 50)
            return True

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


if __name__ == "__main__":
    verify_tables()
