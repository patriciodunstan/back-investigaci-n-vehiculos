#!/bin/bash
set -e

# Ejecutar migraciones de base de datos
echo "📊 Ejecutando migraciones de base de datos..."
alembic upgrade head

# Ejecutar el comando pasado como argumento
exec "$@"
