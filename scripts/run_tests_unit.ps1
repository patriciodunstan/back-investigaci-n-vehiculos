# Script PowerShell para ejecutar solo tests unitarios

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Ejecutando tests unitarios" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

pytest tests/unit/ -v -m "not integration"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Tests unitarios completados" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

