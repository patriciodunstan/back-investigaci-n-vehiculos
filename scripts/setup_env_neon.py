"""
Script para configurar .env con la Connection String de Neon.

Este script crea o actualiza el archivo .env con la configuración de Neon.
"""

import os
from pathlib import Path
import secrets


def generate_secret_key():
    """Genera una clave secreta segura de 64 caracteres."""
    return secrets.token_urlsafe(48)


def setup_env_file(neon_connection_string: str):
    """Configura el archivo .env con la Connection String de Neon."""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    # Generar SECRET_KEY si no existe
    secret_key = generate_secret_key()

    # Contenido del .env
    env_content = f"""# ==================== ENVIRONMENT ====================
ENVIRONMENT=production
DEBUG=false
APP_NAME=Sistema de Investigaciones Vehiculares

# ==================== DATABASE ====================
# Connection String de Neon PostgreSQL 17
DATABASE_URL={neon_connection_string}

# ==================== SECURITY ====================
# Clave secreta generada automáticamente (cambiar en producción)
SECRET_KEY={secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ==================== REDIS ====================
# Configurar si usas Redis (opcional para desarrollo)
REDIS_URL=redis://localhost:6379/0

# ==================== CORS ====================
# Agregar tus dominios frontend aquí
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# ==================== EMAIL ====================
# Configurar si necesitas enviar emails
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@investigaciones.cl
SMTP_FROM_NAME=Sistema Investigaciones

# ==================== STORAGE ====================
STORAGE_TYPE=local
STORAGE_PATH=./storage
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=["image/jpeg","image/png","application/pdf"]

# ==================== LOGGING ====================
LOG_LEVEL=INFO
"""

    # Escribir archivo
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)

    print("=" * 60)
    print("[OK] Archivo .env configurado exitosamente")
    print("=" * 60)
    print(f"\n[INFO] Ubicacion: {env_file}")
    print(f"\n[INFO] SECRET_KEY generada: {secret_key[:20]}...")
    print(f"\n[INFO] DATABASE_URL configurada para Neon")
    print("\n" + "=" * 60)
    print("[PASOS] Proximos pasos:")
    print("   1. Verificar conexion: python scripts/setup_neon.py")
    print("   2. Ejecutar migraciones: alembic upgrade head")
    print("   3. Crear usuario admin: python scripts/seed_admin.py")
    print("=" * 60)


if __name__ == "__main__":
    # Connection String de Neon proporcionada
    neon_connection_string = (
        "postgresql://neondb_owner:npg_Oth8lSLiGQE2@ep-still-cherry-a43un5fs-pooler.us-east-1.aws.neon.tech/"
        "investigaciones_db?sslmode=require&channel_binding=require"
    )

    print("=" * 60)
    print("CONFIGURANDO .env CON NEON POSTGRESQL")
    print("=" * 60)

    # Verificar si .env ya existe
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        print("\n[INFO] El archivo .env ya existe. Se sobrescribira con la configuracion de Neon.")
        # Hacer backup
        backup_file = project_root / ".env.backup"
        if backup_file.exists():
            backup_file.unlink()
        import shutil

        shutil.copy(env_file, backup_file)
        print(f"[INFO] Backup guardado en: .env.backup")

    setup_env_file(neon_connection_string)
