# Script PowerShell para ejecutar todos los tests

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Ejecutando todos los tests" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html:htmlcov

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Tests completados" -ForegroundColor Green
Write-Host "Reporte de coverage en: htmlcov/index.html" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

