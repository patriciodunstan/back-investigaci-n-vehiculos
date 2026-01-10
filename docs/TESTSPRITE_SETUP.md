# Configuración de TestSprite MCP

TestSprite es un agente de testing automatizado con IA que se integra directamente en VS Code.

## ✅ Instalación Completada

Se ha configurado:
- `.vscode/mcp.json` - Configuración del servidor MCP
- `.env` - Variable `TESTSPRITE_API_KEY` agregada

## 🔑 Paso 1: Obtener API Key

1. Registrarse en [TestSprite](https://www.testsprite.com/auth/cognito/sign-up) (gratis)
2. Ir a [Dashboard > Settings > API Key](https://www.testsprite.com/dashboard/settings/apikey)
3. Copiar tu API Key

## 🔧 Paso 2: Configurar API Key

Editar el archivo `.env` y agregar tu API Key:

```env
TESTSPRITE_API_KEY=tu-api-key-aquí
```

## 🚀 Paso 3: Reiniciar VS Code

Después de configurar la API Key, reinicia VS Code para que el servidor MCP se conecte.

## 📋 Uso

Una vez configurado, en el chat de Copilot puedes decir:

```
Help me test this project with TestSprite
```

O en español:

```
Ayúdame a testear este proyecto con TestSprite
```

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `test this project` | Genera y ejecuta tests para todo el proyecto |
| `test this file` | Testea el archivo actual |
| `test this endpoint` | Testea un endpoint específico |

## 🎯 Qué Testea TestSprite

Para tu proyecto FastAPI, TestSprite puede generar:

- **Tests de API REST** - Todos los endpoints de oficios, usuarios, buffets, etc.
- **Tests de autenticación** - Login, JWT, permisos
- **Tests de validación** - Schemas Pydantic, datos inválidos
- **Tests de edge cases** - Casos límite, errores 404, 422, etc.
- **Tests de seguridad** - Vulnerabilidades comunes

## 📊 Ejemplo de Salida

```
TestSprite Analysis Complete

Generated:
├── 24 Backend API Test Cases
├── 8 Authentication Tests
├── 12 Validation Tests
├── Test Execution Reports
└── Comprehensive Test Plan

Coverage: 85%+ Endpoints Covered
```

## 🔗 Recursos

- [Documentación](https://docs.testsprite.com/)
- [Video Demo 10 min](https://youtu.be/yLQdORqPl3s)
- [Discord Community](https://discord.com/invite/QQB9tJ973e)
