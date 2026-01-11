import sys
import asyncio

sys.path.insert(0, ".")

from sqlalchemy import text
from src.core.config import get_settings
from src.shared.infrastructure.database import engine, AsyncSessionLocal


async def test_connection():
    """Prueba la conexión a PostgreSQL"""
    settings = get_settings()

    print(f"🔌 Conectando a: {settings.DATABASE_URL}")

    try:
        # Probar conexión
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a PostgreSQL")

        # Probar sesión
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📦 Versión de PostgreSQL: {version[:50]}...")

        print("\n✅ Todo funcionando correctamente!")
        return True

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Asegúrate de que:")
        print("   1. Docker esté corriendo: docker-compose up -d db")
        print("   2. El archivo .env esté configurado correctamente")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())
