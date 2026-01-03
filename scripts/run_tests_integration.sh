#!/bin/bash
# Script para ejecutar solo tests de integración

echo "=========================================="
echo "Ejecutando tests de integración"
echo "=========================================="

pytest tests/integration/ -v -m integration

echo ""
echo "=========================================="
echo "Tests de integración completados"
echo "=========================================="

