# Guía para Obtener Credenciales de Google Drive

Esta guía te ayudará a configurar las credenciales necesarias para la integración con Google Drive.

## 📋 Requisitos Previos

- Cuenta de Google (Gmail o Google Workspace)
- Acceso a Google Cloud Console
- Permisos para crear proyectos y habilitar APIs

---

## 🔧 Paso 1: Crear Proyecto en Google Cloud Console

1. **Accede a Google Cloud Console**
   - Ve a: https://console.cloud.google.com/
   - Inicia sesión con tu cuenta de Google

2. **Crear un nuevo proyecto**
   - Haz clic en el selector de proyectos (arriba a la izquierda)
   - Haz clic en "NUEVO PROYECTO"
   - Nombre del proyecto: `investigaciones-vehiculares` (o el que prefieras)
   - Organización: Dejar en blanco (o seleccionar si tienes)
   - Haz clic en "CREAR"

3. **Seleccionar el proyecto**
   - Asegúrate de que el proyecto recién creado esté seleccionado

---

## 🔑 Paso 2: Habilitar Google Drive API

1. **Navegar a la Biblioteca de APIs**
   - En el menú lateral, ve a: **APIs y servicios > Biblioteca**
   - O directamente: https://console.cloud.google.com/apis/library

2. **Buscar y habilitar Google Drive API**
   - Busca: "Google Drive API"
   - Haz clic en el resultado
   - Haz clic en el botón **"HABILITAR"**
   - Espera a que se habilite (puede tomar unos segundos)

---

## 👤 Paso 3: Crear Service Account

Para esta integración, usamos una **Service Account** (cuenta de servicio), que es la forma recomendada para aplicaciones server-to-server.

1. **Navegar a Credenciales**
   - En el menú lateral, ve a: **APIs y servicios > Credenciales**
   - O directamente: https://console.cloud.google.com/apis/credentials

2. **Crear Service Account**
   - Haz clic en **"+ CREAR CREDENCIALES"** (arriba)
   - Selecciona **"Cuenta de servicio"**
   - Si no ves esta opción, haz clic en **"Gestionar cuentas de servicio"** y luego **"+ CREAR CUENTA DE SERVICIO"**

3. **Configurar Service Account**
   - **Nombre de la cuenta de servicio**: `drive-integration` (o el que prefieras)
   - **ID de cuenta de servicio**: Se genera automáticamente (puedes cambiarlo)
   - **Descripción**: "Cuenta de servicio para integración con Google Drive"
   - Haz clic en **"CREAR Y CONTINUAR"**

4. **Asignar roles (opcional)**
   - Por ahora, puedes saltar este paso
   - Haz clic en **"CONTINUAR"**

5. **Finalizar**
   - Haz clic en **"LISTO"**

---

## 📥 Paso 4: Crear y Descargar Key JSON

1. **Acceder a la Service Account creada**
   - En la lista de cuentas de servicio, haz clic en la que acabas de crear (`drive-integration`)

2. **Crear Key JSON**
   - Ve a la pestaña **"CLAVES"**
   - Haz clic en **"AGREGAR CLAVE"** > **"Crear nueva clave"**
   - Selecciona formato **JSON**
   - Haz clic en **"CREAR"**
   - **El archivo JSON se descargará automáticamente** ⚠️ **GUARDA ESTE ARCHIVO DE FORMA SEGURA**

3. **Estructura del archivo JSON**
   El archivo descargado tendrá esta estructura:
   ```json
   {
     "type": "service_account",
     "project_id": "tu-proyecto-id",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "drive-integration@tu-proyecto.iam.gserviceaccount.com",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "..."
   }
   ```

---

## 🔐 Paso 5: Compartir Carpeta de Google Drive con Service Account

⚠️ **IMPORTANTE:** Google limita compartir carpetas con Service Accounts desde cuentas personales (gmail.com). 

**Si tienes una cuenta personal de Google (gmail.com):**
- Google tiene un límite muy estricto (a veces 0) para compartir con Service Accounts
- Ver sección "Solución de Problemas" más abajo para alternativas

**Si tienes Google Workspace (cuenta empresarial):**
- Puedes compartir normalmente con Service Accounts
- Sigue los pasos a continuación

### Opción A: Compartir desde Google Workspace (Recomendado)

1. **Obtener el email de la Service Account**
   - En la página de la Service Account, copia el **"Correo electrónico"**
   - Formato: `drive-integration@tu-proyecto-id.iam.gserviceaccount.com`

2. **Compartir carpeta en Google Drive**
   - Abre Google Drive: https://drive.google.com/
   - Ve a la carpeta que quieres monitorear (o créala)
   - Haz clic derecho en la carpeta > **"Compartir"**
   - En el campo de búsqueda, pega el email de la Service Account
   - Selecciona **"Lector"** como permiso (solo lectura es suficiente)
   - **NO marques** "Notificar a las personas"
   - Haz clic en **"Compartir"**

3. **Obtener el ID de la carpeta**
   - Abre la carpeta en Google Drive
   - Mira la URL en el navegador:
     ```
     https://drive.google.com/drive/folders/ABC123XYZ789
     ```
   - El ID es la parte después de `/folders/`: `ABC123XYZ789`
   - **Copia este ID** (lo necesitarás para la configuración)

---

## ⚙️ Paso 6: Configurar Variables de Entorno

Ahora necesitas configurar las variables de entorno en tu proyecto.

### Opción A: JSON como String (Recomendado para producción)

1. **Leer el contenido del archivo JSON**
   - Abre el archivo JSON descargado
   - Copia TODO su contenido (incluyendo llaves, comillas, etc.)

2. **Agregar al archivo `.env`**
   ```env
   # Google Drive Integration
   GOOGLE_DRIVE_ENABLED=true
   GOOGLE_DRIVE_FOLDER_ID=ABC123XYZ789
   GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key":"..."}
   GOOGLE_DRIVE_WEBHOOK_SECRET=tu_secreto_aleatorio_aqui
   ```
   
   **⚠️ IMPORTANTE:** 
   - El JSON debe estar en una sola línea
   - O usa comillas triples si tu sistema lo soporta
   - En Windows PowerShell, puedes necesitar escapar las comillas

### Opción B: JSON como Path a Archivo (Recomendado para desarrollo local)

1. **Guardar el archivo JSON en un lugar seguro**
   - Por ejemplo: `./config/google-drive-service-account.json`
   - **⚠️ IMPORTANTE:** Agrega este archivo a `.gitignore` para no subirlo a git

2. **Agregar al archivo `.env`**
   ```env
   # Google Drive Integration
   GOOGLE_DRIVE_ENABLED=true
   GOOGLE_DRIVE_FOLDER_ID=ABC123XYZ789
   GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON=./config/google-drive-service-account.json
   GOOGLE_DRIVE_WEBHOOK_SECRET=tu_secreto_aleatorio_aqui
   ```

### Opción C: Usar Variable de Entorno del Sistema

En algunos entornos (como Render, Heroku, etc.), puedes configurar la variable directamente:

```bash
export GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
```

---

## 📝 Paso 7: Configurar Mapeo de Carpetas a Buffets (Opcional)

Si quieres mapear diferentes carpetas de Google Drive a diferentes buffets:

1. **Crear archivo JSON de mapeo**
   ```json
   {
     "ABC123XYZ789": 1,
     "DEF456UVW012": 2,
     "GHI789RST345": 3
   }
   ```

2. **Agregar al `.env`**
   ```env
   GOOGLE_DRIVE_BUFFET_MAPPING={"ABC123XYZ789":1,"DEF456UVW012":2}
   ```

   O como path a archivo:
   ```env
   GOOGLE_DRIVE_BUFFET_MAPPING=./config/buffet-mapping.json
   ```

---

## 🔒 Paso 8: Configurar Webhook Secret (Opcional)

Para validar webhooks de Google Drive (si los implementas):

1. **Generar un secreto aleatorio**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Agregar al `.env`**
   ```env
   GOOGLE_DRIVE_WEBHOOK_SECRET=tu_secreto_generado_aqui
   ```

---

## ✅ Paso 9: Verificar Configuración

1. **Instalar dependencias**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Probar conexión**
   Puedes crear un script de prueba:
   ```python
   from src.shared.infrastructure.external_apis.google_drive import get_google_drive_client
   
   async def test():
       client = get_google_drive_client()
       files = await client.list_files("TU_FOLDER_ID")
       print(f"Archivos encontrados: {len(files.files)}")
   ```

---

## 🔍 Solución de Problemas

### Error: "Has superado la cuota de elementos compartidos" (Cuenta Personal Gmail)

Este es el problema más común. Google limita (a veces a 0) compartir carpetas con Service Accounts desde cuentas personales.

**Soluciones:**

#### Solución 1: Usar Google Workspace (Recomendado)
- Si tienes acceso a Google Workspace (cuenta empresarial), usa esa cuenta
- Google Workspace permite compartir sin problemas con Service Accounts
- Crea la carpeta en el Drive de Google Workspace y compártela normalmente

#### Solución 2: Compartir con un Usuario Normal + OAuth 2.0
Si no tienes Google Workspace, puedes:
1. Crear la carpeta en tu cuenta personal
2. Compartirla con un usuario normal (no Service Account)
3. Usar OAuth 2.0 en lugar de Service Account (requiere autenticación del usuario)

**Nota:** Esto requeriría cambiar la implementación para usar OAuth 2.0 en lugar de Service Account.

#### Solución 3: Usar Domain-Wide Delegation (Avanzado)
- Solo funciona con Google Workspace
- Requiere configuración adicional en el admin de Google Workspace
- Más complejo pero más robusto

#### Solución 4: Cuenta de Prueba con Google Workspace
- Crear una cuenta de Google Workspace (hay planes gratuitos de prueba)
- Usar esa cuenta para el proyecto

**Recomendación:** Si es para producción, usa Google Workspace. Si es para desarrollo/testing, considera la Solución 2 o crear una cuenta de prueba.

### Error: "GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON no configurado"
- Verifica que la variable esté en el `.env`
- Verifica que el archivo JSON exista (si usas path)
- Verifica que el JSON sea válido

### Error: "Permisos insuficientes"
- Verifica que la Service Account tenga acceso a la carpeta
- Verifica que el email de la Service Account sea correcto
- Verifica que la carpeta esté compartida con permisos de "Lector" o superior
- Si usas cuenta personal, verifica que no hayas alcanzado el límite

### Error: "ModuleNotFoundError: No module named 'google'"
- Instala las dependencias: `pip install google-auth google-auth-oauthlib google-api-python-client`

### Error: "Invalid JSON"
- Verifica que el JSON esté completo
- Si usas string en .env, puede necesitar escapado de comillas
- Considera usar path a archivo en lugar de string

---

## 📚 Recursos Adicionales

- [Documentación de Google Drive API](https://developers.google.com/drive/api)
- [Guía de Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Guía de autenticación](https://cloud.google.com/docs/authentication)

---

## 🔐 Seguridad

**⚠️ IMPORTANTE:**
- **NUNCA** subas el archivo JSON de Service Account a git
- Agrega `*.json` de credenciales a `.gitignore`
- Usa variables de entorno en producción
- Rota las keys periódicamente
- Limita los permisos de la Service Account al mínimo necesario

---

## 📝 Checklist Final

- [ ] Proyecto creado en Google Cloud Console
- [ ] Google Drive API habilitada
- [ ] Service Account creada
- [ ] Key JSON descargada y guardada de forma segura
- [ ] Carpeta compartida con Service Account
- [ ] ID de carpeta copiado
- [ ] Variables de entorno configuradas en `.env`
- [ ] Dependencias instaladas
- [ ] Conexión probada y funcionando
