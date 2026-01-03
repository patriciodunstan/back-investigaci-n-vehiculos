#!/bin/bash
# Script para ejecutar todos los tests

echo "=========================================="
echo "Ejecutando todos los tests"
echo "=========================================="

pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html:htmlcov

echo ""
echo "=========================================="
echo "Tests completados"
echo "Reporte de coverage en: htmlcov/index.html"
echo "=========================================="

