"""
Script para generar una SECRET_KEY segura para producción.

Ejecutar: python scripts/generate_secret_key.py
"""

import secrets


def generate_secret_key():
    """Genera una clave secreta segura de 64 caracteres."""
    return secrets.token_urlsafe(48)


if __name__ == "__main__":
    key = generate_secret_key()
    print("=" * 60)
    print("SECRET_KEY GENERADA")
    print("=" * 60)
    print(f"\n{key}\n")
    print("=" * 60)
    print("Copia esta clave y configurala en Render como:")
    print("SECRET_KEY=<la-clave-generada>")
    print("=" * 60)
