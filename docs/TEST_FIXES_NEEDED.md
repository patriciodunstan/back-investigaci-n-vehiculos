# 🔧 Correcciones Necesarias en Tests

Este documento lista todos los problemas encontrados en los tests y sus soluciones.

## ✅ Problemas Corregidos

1. **`conftest.py` - Asignación de campos inmutables**
   - ✅ Corregido: Usar `object.__setattr__()` para asignar `created_at` y `updated_at`

2. **`Usuario.crear()` - Parámetro `activo`**
   - ✅ Corregido: Agregado parámetro opcional `activo: bool = True` a `Usuario.crear()`

## ⚠️ Problemas Pendientes

### 1. `BaseEntity.marcar_actualizado()` - Asignación incorrecta

**Problema:**
```python
def marcar_actualizado(self) -> None:
    object.__setattr__(self, "update_at", datetime.now)  # ❌ Asigna la función, no el resultado
```

**Solución:**
```python
def marcar_actualizado(self) -> None:
    object.__setattr__(self, "update_at", datetime.now())  # ✅ Llamar la función
```

### 2. Tests que comparan `updated_at` como método

**Problema:**
Los tests comparan `updated_at` directamente, pero es una propiedad que retorna `update_at`.

**Solución:**
Los tests deben comparar el valor correctamente:
```python
original_updated_at = usuario.updated_at  # Obtener el valor
usuario.actualizar_perfil(nombre="Nuevo")
assert usuario.updated_at > original_updated_at  # Comparar valores
```

### 3. Tests que esperan RUT sin puntos

**Problema:**
Los tests esperan `"12345678-5"` pero `RutChileno` formatea como `"12.345.678-5"`.

**Solución:**
Actualizar los tests para esperar el formato correcto, o usar `rut_str` que puede tener formato diferente.

### 4. Mensajes de excepción no coinciden

**Problema:**
Los tests esperan mensajes específicos que no coinciden con los mensajes reales.

**Solución:**
Actualizar los tests para usar los mensajes reales de las excepciones, o actualizar las excepciones para usar los mensajes esperados.

### 5. Tests de integración - Tablas no creadas

**Problema:**
Los tests de integración fallan porque las tablas no están creadas antes de ejecutar los tests.

**Solución:**
Asegurar que `test_client` fixture cree las tablas antes de ejecutar los tests.

### 6. Password Hasher - Contraseñas > 72 bytes

**Problema:**
Bcrypt tiene un límite de 72 bytes para contraseñas.

**Solución:**
Truncar o hash la contraseña antes de pasarla a bcrypt si es > 72 bytes.

### 7. Tests que usan métodos inexistentes

**Problema:**
Algunos tests llaman métodos que no existen (ej: `cambiar_contrasena`).

**Solución:**
Implementar los métodos faltantes o actualizar los tests para usar los métodos correctos.

### 8. Tests de excepciones - Parámetros faltantes

**Problema:**
Algunas excepciones requieren parámetros que los tests no proporcionan.

**Solución:**
Actualizar los tests para proporcionar los parámetros requeridos.

## 📝 Prioridad de Corrección

1. **Alta**: `BaseEntity.marcar_actualizado()` - Afecta todas las entidades
2. **Alta**: Tests de integración - Tablas no creadas
3. **Media**: Mensajes de excepción
4. **Media**: Comparaciones de `updated_at`
5. **Baja**: Formato de RUT en tests
6. **Baja**: Password hasher para contraseñas largas

