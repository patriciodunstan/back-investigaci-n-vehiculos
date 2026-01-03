#!/bin/bash
# Script de build para Render
# Este script se ejecuta durante el build en Render

set -e  # Salir si hay algún error

echo "=========================================="
echo "Build para Render"
echo "=========================================="

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📊 Ejecutando migraciones..."
# Verificar que DATABASE_URL esté configurada
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  ADVERTENCIA: DATABASE_URL no está configurada"
    echo "   Las migraciones se saltarán"
else
    alembic upgrade head
    echo "✅ Migraciones ejecutadas"
fi

echo ""
echo "=========================================="
echo "✅ Build completado"
echo "=========================================="

