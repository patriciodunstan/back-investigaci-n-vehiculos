import sys

sys.path.insert(0, ".")

from sqlalchemy import text
from src.core.config import get_settings
from src.shared.infrastructure.database import engine, SessionLocal


def test_connection():
    """Prueba la conexión a PostgreSQL"""
    settings = get_settings()

    print(f"🔌 Conectando a: {settings.DATABASE_URL}")

    try:
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a PostgreSQL")

        # Probar sesión
        db = SessionLocal()
        version = db.execute(text("SELECT version()")).fetchone()[0]
        print(f"📦 Versión de PostgreSQL: {version[:50]}...")
        db.close()

        print("\n✅ Todo funcionando correctamente!")
        return True

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Asegúrate de que:")
        print("   1. Docker esté corriendo: docker-compose up -d db")
        print("   2. El archivo .env esté configurado correctamente")
        return False


if __name__ == "__main__":
    test_connection()
