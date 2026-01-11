# Fix: Tests ERROR en CI Pipeline

## Problema

Los tests en CI están fallando con ERROR (no FAILED) después del primer test. Esto indica un problema en el setup/fixtures antes de que los tests se ejecuten.

## Causa Probable

El enfoque actual de crear/eliminar tablas para cada test (`create_all` / `drop_all`) puede causar problemas en PostgreSQL:
- Locks en tablas del sistema
- Conexiones no cerradas correctamente
- Problemas con transacciones

## Solución Recomendada

Usar un enfoque más robusto:
1. Crear tablas una vez (al inicio)
2. Limpiar datos con transacciones que se revierten (ROLLBACK)
3. O usar TRUNCATE para limpiar datos

Esto es más eficiente y evita problemas de locks en PostgreSQL.
