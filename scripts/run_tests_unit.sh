#!/bin/bash
# Script para ejecutar solo tests unitarios

echo "=========================================="
echo "Ejecutando tests unitarios"
echo "=========================================="

pytest tests/unit/ -v -m "not integration"

echo ""
echo "=========================================="
echo "Tests unitarios completados"
echo "=========================================="

