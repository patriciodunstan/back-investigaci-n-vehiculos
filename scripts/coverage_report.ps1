# Script PowerShell para generar reporte de coverage

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Generando reporte de coverage" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

pytest tests/ --cov=src --cov-report=html:htmlcov --cov-report=term-missing

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Reporte generado en: htmlcov/index.html" -ForegroundColor Green
Write-Host "Abrir con: Start-Process htmlcov/index.html" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

