# Guía de Setup Git

Pasos para configurar el repositorio Git y hacer el primer commit.

## 📋 Verificar Estado

```bash
git status
```

Deberías ver:
- ✅ Archivos de código listos para commit
- ✅ `.env` y otros archivos sensibles ignorados
- ✅ `__pycache__/` y otros archivos temporales ignorados

## 🚀 Primer Commit

### 1. Agregar todos los archivos

```bash
git add .
```

### 2. Verificar qué se va a commitear

```bash
git status
```

**IMPORTANTE**: Verifica que NO aparezcan:
- ❌ `.env` (debe estar ignorado)
- ❌ `venv/` o `.env_new/` (deben estar ignorados)
- ❌ `__pycache__/` (debe estar ignorado)
- ❌ Archivos con passwords o secrets

### 3. Hacer el commit inicial

```bash
git commit -m "feat: implementación inicial del sistema de investigaciones vehiculares

- Arquitectura Clean Architecture con Modular Monolith
- Módulos: Usuarios, Buffets, Oficios, Investigaciones, Notificaciones
- Autenticación JWT
- Base de datos PostgreSQL 17 con Alembic
- Tests unitarios y de integración
- Documentación completa
- Configuración para Neon y Render"
```

### 4. Configurar repositorio remoto (si aún no está configurado)

```bash
# Si es GitHub
git remote add origin https://github.com/tu-usuario/tu-repo.git

# O si es GitLab
git remote add origin https://gitlab.com/tu-usuario/tu-repo.git
```

### 5. Push al repositorio

```bash
git branch -M main
git push -u origin main
```

## 🔒 Archivos que NUNCA deben subirse

El `.gitignore` ya está configurado para ignorar:

- ✅ `.env` - Variables de entorno con secrets
- ✅ `*.key`, `*.pem` - Claves privadas
- ✅ `venv/`, `.env_new/` - Entornos virtuales
- ✅ `__pycache__/` - Archivos Python compilados
- ✅ `.coverage`, `htmlcov/` - Reportes de coverage
- ✅ `storage/` - Archivos subidos localmente
- ✅ `*.log` - Archivos de log

## ✅ Checklist antes de commitear

- [ ] `.env` está en `.gitignore` y no aparece en `git status`
- [ ] No hay passwords o secrets en el código
- [ ] `requirements.txt` está actualizado
- [ ] `README.md` está completo
- [ ] Tests pasan: `pytest`
- [ ] No hay archivos temporales o de cache

## 📝 Comandos útiles

### Ver qué archivos están siendo ignorados

```bash
git status --ignored
```

### Verificar que un archivo específico está ignorado

```bash
git check-ignore -v .env
```

### Agregar un archivo que está siendo ignorado (si es necesario)

```bash
git add -f archivo_especifico.py
```

### Ver diferencias antes de commitear

```bash
git diff --cached
```

## 🐛 Troubleshooting

### Error: "fatal: not a git repository"

Inicializa el repositorio:

```bash
git init
```

### Archivo `.env` aparece en git status

Verifica que esté en `.gitignore`:

```bash
# Verificar
git check-ignore -v .env

# Si no está ignorado, agregar al .gitignore
echo ".env" >> .gitignore
git rm --cached .env  # Remover del índice si ya estaba trackeado
```

### Quitar archivos ya trackeados del repositorio

```bash
# Remover archivo del índice pero mantenerlo localmente
git rm --cached archivo.txt

# Remover directorio completo
git rm -r --cached directorio/
```

