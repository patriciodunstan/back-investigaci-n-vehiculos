# TestSprite AI Testing Report

---

## 1️⃣ Document Metadata
- **Project Name:** back-investigación-vehiculos
- **Date:** 2026-01-08
- **Prepared by:** TestSprite AI Team + GitHub Copilot

---

## 2️⃣ Executive Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 10 |
| **Passed** | 1 (10%) |
| **Failed** | 9 (90%) |
| **Root Cause** | Formato de login incorrecto |

### 🔴 Problema Principal Identificado

Todos los tests fallan en el endpoint `/api/v1/auth/login` con error **422 Unprocessable Entity**.

**Causa raíz:** El endpoint de login espera `username` y `password` en formato **form-data** (OAuth2), pero los tests generados envían `email` y `password` en formato **JSON**.

```
{"detail":[
  {"type":"missing","loc":["body","username"],"msg":"Field required"},
  {"type":"missing","loc":["body","password"],"msg":"Field required"}
]}
```

---

## 3️⃣ Requirement Validation Summary

### ✅ Authentication - Register (1/3 Passed)

#### Test TC001 - ✅ PASSED
- **Test Name:** register new user with valid data
- **Status:** ✅ Passed
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/3a17e1cc-ae0a-4095-b9e7-deb36f6900b0)
- **Analysis:** El endpoint de registro funciona correctamente con JSON body.

---

### ❌ Authentication - Login (2/3 Failed)

#### Test TC002 - ❌ FAILED
- **Test Name:** login user with correct credentials
- **Status:** ❌ Failed
- **Error:** `AssertionError: Expected status 200, got 422`
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/bd1699ad-c06a-4dfd-9af7-de7cefcd2f2f)
- **Analysis:** El test envía JSON, pero el endpoint espera form-data con `username` (no `email`).

#### Test TC003 - ❌ FAILED
- **Test Name:** get current user with valid token
- **Status:** ❌ Failed
- **Error:** `AssertionError: Login failed with status 422`
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/5522d0a3-7d2e-4f4f-8d8b-d530588d08ff)
- **Analysis:** Falla en pre-condición (login requerido para obtener token).

---

### ❌ Buffets Management (0/4 Passed)

#### Test TC004 - ❌ FAILED
- **Test Name:** create buffet as admin user
- **Error:** `AssertionError: Admin login failed with status 422`
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/8737ba3b-7307-4219-912d-48364bb65199)
- **Analysis:** No puede autenticarse como admin para probar el endpoint.

#### Test TC005 - ❌ FAILED
- **Test Name:** list buffets with pagination and active filter
- **Error:** Login failed - missing `username` field
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/063a8b89-5e0f-41b4-88fe-163f2468fede)
- **Analysis:** Mismo problema de formato de login.

#### Test TC006 - ❌ FAILED
- **Test Name:** get buffet by id
- **Error:** `HTTPError: 422 Client Error for /api/v1/auth/login`
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/ca74a655-5305-4baa-bf34-b2beb0ef2662)
- **Analysis:** Bloqueado por fallo de autenticación.

#### Test TC007 - ❌ FAILED
- **Test Name:** update buffet as admin user
- **Error:** `HTTPError: 422 Client Error for /api/v1/auth/login`
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/c2ace078-9cbe-49a0-9f82-ab3123e92b31)
- **Analysis:** Bloqueado por fallo de autenticación.

#### Test TC008 - ❌ FAILED
- **Test Name:** soft delete buffet as admin user
- **Error:** `HTTPError: 422 Client Error for /api/v1/auth/login`
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/9af4d0cb-783b-4912-b66c-f850a64edca9)
- **Analysis:** Bloqueado por fallo de autenticación.

---

### ❌ Oficios Management (0/1 Passed)

#### Test TC009 - ❌ FAILED
- **Test Name:** list oficios with filters and pagination
- **Error:** `AssertionError: Login failed with status 422`
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/79b994d9-3d6d-45e8-9f5e-6268380e76b5)
- **Analysis:** Bloqueado por fallo de autenticación.

---

### ❌ Address Verification (0/1 Passed)

#### Test TC010 - ❌ FAILED
- **Test Name:** register visit to address
- **Error:** `HTTPError: 422 Client Error for /api/v1/auth/login`
- **Visualization:** [Ver en TestSprite](https://www.testsprite.com/dashboard/mcp/tests/8a0ee666-6eef-428a-903d-ec6a0eccee7b/b619ca1b-4737-444d-8934-1ff8697d43b8)
- **Analysis:** Bloqueado por fallo de autenticación.

---

## 4️⃣ Coverage & Matching Metrics

| Requirement | Total Tests | ✅ Passed | ❌ Failed |
|-------------|-------------|-----------|-----------|
| Authentication - Register | 1 | 1 | 0 |
| Authentication - Login | 2 | 0 | 2 |
| Buffets Management | 5 | 0 | 5 |
| Oficios Management | 1 | 0 | 1 |
| Address Verification | 1 | 0 | 1 |
| **TOTAL** | **10** | **1** | **9** |

---

## 5️⃣ Key Gaps / Risks

### 🔴 Critical: Formato de Login Incompatible

**Problema:** El endpoint `/api/v1/auth/login` implementa OAuth2PasswordRequestForm que requiere:
- Content-Type: `application/x-www-form-urlencoded`
- Campos: `username` y `password` (no `email`)

**Los tests generados asumen:**
- Content-Type: `application/json`
- Campos: `email` y `password`

### 📋 Opciones de Solución

#### Opción A: Modificar el PRD para TestSprite
Actualizar la documentación del API para especificar el formato correcto de login.

#### Opción B: Agregar endpoint JSON alternativo
Crear `/api/v1/auth/login/json` que acepte JSON con `email`/`password`.

#### Opción C: Modificar el endpoint existente
Hacer que `/api/v1/auth/login` acepte ambos formatos (form-data y JSON).

---

## 6️⃣ Recommendations

1. **Corto plazo:** Actualizar el code_summary.json para indicar que login usa form-data con `username`
2. **Re-ejecutar tests** después de corregir la documentación
3. **Considerar** agregar soporte JSON al login para mayor compatibilidad con clientes REST

---

## 7️⃣ Test Artifacts

- [Código TC001](./TC001_register_new_user_with_valid_data.py)
- [Código TC002](./TC002_login_user_with_correct_credentials.py)
- [Código TC003](./TC003_get_current_user_with_valid_token.py)
- [Código TC004](./TC004_create_buffet_as_admin_user.py)
- [Código TC005](./TC005_list_buffets_with_pagination_and_active_filter.py)
- [Código TC006](./TC006_get_buffet_by_id.py)
- [Código TC007](./TC007_update_buffet_as_admin_user.py)
- [Código TC008](./TC008_soft_delete_buffet_as_admin_user.py)
- [Código TC009](./TC009_list_oficios_with_filters_and_pagination.py)
- [Código TC010](./TC010_register_visit_to_address.py)

---

*Report generated by TestSprite AI + GitHub Copilot*
