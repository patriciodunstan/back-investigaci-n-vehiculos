# Instrucciones para Push

## ✅ Commit Realizado

El commit inicial se ha realizado exitosamente:
- **215 archivos** agregados
- **21,242 líneas** de código
- Commit hash: `603d36d`

## 🚀 Próximos Pasos

### Si ya tienes el repositorio creado:

```bash
# Agregar remote (reemplaza con tu URL)
git remote add origin https://github.com/tu-usuario/tu-repo.git

# O si es GitLab
git remote add origin https://gitlab.com/tu-usuario/tu-repo.git

# Verificar que se agregó correctamente
git remote -v

# Hacer push
git branch -M main
git push -u origin main
```

### Si NO tienes el repositorio creado:

1. **Crea el repositorio** en GitHub/GitLab:
   - Ve a GitHub.com o GitLab.com
   - Click en "New Repository"
   - Nombre: `back-investigación-vehiculos` (o el que prefieras)
   - **NO** inicialices con README, .gitignore, ni licencia (ya los tenemos)

2. **Copia la URL** del repositorio

3. **Ejecuta estos comandos**:

```bash
# Agregar remote
git remote add origin <URL-DE-TU-REPOSITORIO>

# Verificar
git remote -v

# Push
git branch -M main
git push -u origin main
```

## 🔍 Verificar Estado

```bash
# Ver commits locales
git log --oneline

# Ver estado
git status

# Ver remotes configurados
git remote -v
```

## ⚠️ Si hay errores

### Error: "remote origin already exists"

```bash
# Ver el remote actual
git remote -v

# Si quieres cambiarlo
git remote set-url origin <NUEVA-URL>

# O removerlo y agregar uno nuevo
git remote remove origin
git remote add origin <URL>
```

### Error: "failed to push some refs"

```bash
# Si el repositorio remoto tiene contenido, primero haz pull
git pull origin main --allow-unrelated-histories

# Luego push
git push -u origin main
```

