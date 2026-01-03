# PostgreSQL 17 - Notas de Compatibilidad

Este proyecto está configurado para usar **PostgreSQL 17**.

## ✅ Compatibilidad

### Dependencias Verificadas

- ✅ **psycopg2-binary==2.9.9**: Compatible con PostgreSQL 17
- ✅ **SQLAlchemy 2.0.25**: Compatible con PostgreSQL 17
- ✅ **Alembic 1.13.1**: Compatible con PostgreSQL 17
- ✅ **asyncpg==0.29.0**: Compatible con PostgreSQL 17

### Características de PostgreSQL 17

PostgreSQL 17 incluye mejoras en:
- Performance y optimización de queries
- Mejor manejo de conexiones
- Nuevas funciones SQL
- Mejoras en índices y particionamiento

## 🔧 Configuración en Neon

Al crear tu proyecto en Neon:

1. Selecciona **PostgreSQL 17** en el selector de versión
2. Si no está disponible, selecciona la versión más reciente disponible
3. El código es compatible con PostgreSQL 15+ si necesitas usar una versión anterior

## 📝 Notas Importantes

### SSL/TLS

Neon requiere SSL para todas las conexiones. Asegúrate de incluir `sslmode=require` en tu Connection String:

```
postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

### Connection Pooling

PostgreSQL 17 tiene mejoras en el manejo de conexiones. El código ya está configurado con:

- `pool_size=10`: Conexiones base en el pool
- `max_overflow=20`: Conexiones adicionales permitidas
- `pool_pre_ping=True`: Verifica conexiones antes de usarlas

### Migraciones

Las migraciones de Alembic funcionan sin cambios con PostgreSQL 17. Ejecuta:

```bash
alembic upgrade head
```

## 🐛 Troubleshooting

### Error: "unsupported PostgreSQL version"

Si encuentras este error, verifica:
1. Que estés usando `psycopg2-binary>=2.9.9`
2. Que SQLAlchemy esté actualizado
3. Que la versión de PostgreSQL sea realmente 17

### Verificar Versión

Puedes verificar la versión de PostgreSQL con:

```sql
SELECT version();
```

O usando el script de setup:

```bash
python scripts/setup_neon.py
```

## 🔗 Recursos

- [PostgreSQL 17 Release Notes](https://www.postgresql.org/docs/17/release-17.html)
- [Neon PostgreSQL Versions](https://neon.tech/docs/introduction/postgres-versions)
- [psycopg2 Compatibility](https://www.psycopg.org/docs/)

