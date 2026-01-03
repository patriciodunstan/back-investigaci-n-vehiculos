# Script PowerShell para ejecutar solo tests de integración

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Ejecutando tests de integración" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

pytest tests/integration/ -v -m integration

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Tests de integración completados" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

