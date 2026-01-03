#!/bin/bash
# Script para generar reporte de coverage

echo "=========================================="
echo "Generando reporte de coverage"
echo "=========================================="

pytest tests/ --cov=src --cov-report=html:htmlcov --cov-report=term-missing

echo ""
echo "=========================================="
echo "Reporte generado en: htmlcov/index.html"
echo "Abrir con: open htmlcov/index.html"
echo "=========================================="

