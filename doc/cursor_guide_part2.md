# PARTE 2: MODELO DE DATOS COMPLETO Y AUTENTICACIÓN

## 5.2 Tablas Detalladas (Continuación)

#### 5.2.3 Oficio (Unidad de Trabajo)

```python
class Oficio(Base):
    __tablename__ = "oficios"
    
    # Campos
    id: int                        # PK
    numero_oficio: str             # Unique, "OF-2024-001"
    buffet_id: int                 # FK a Buffet
    investigador_id: Optional[int] # FK a Usuario (null si no asignado)
    estado: EstadoOficioEnum       # Estado del oficio
    prioridad: PrioridadEnum       # Prioridad
    fecha_ingreso: date            # Fecha de creación
    fecha_limite: Optional[date]   # Deadline
    notas_generales: Optional[str] # Notas generales
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    buffet: Buffet                        # N:1 - Buffet del oficio
    investigador: Optional[Usuario]       # N:1 - Investigador asignado
    vehiculo: Vehiculo                    # 1:1 - Vehículo del oficio
    propietarios: List[Propietario]       # 1:N - Propietarios
    direcciones: List[Direccion]          # 1:N - Direcciones
    investigaciones: List[Investigacion]  # 1:N - Timeline de actividades
    avistamientos: List[Avistamiento]     # 1:N - Resultados de APIs
    adjuntos: List[Adjunto]               # 1:N - Fotos y documentos
    notificaciones: List[Notificacion]    # 1:N - Emails enviados

# Enums
class EstadoOficioEnum(str, Enum):
    PENDIENTE = "pendiente"                      # Recién ingresado
    INVESTIGACION = "investigacion"              # En proceso
    NOTIFICACION = "notificacion"                # Esperando notificación
    FINALIZADO_ENCONTRADO = "finalizado_encontrado"     # Encontrado
    FINALIZADO_NO_ENCONTRADO = "finalizado_no_encontrado"  # No encontrado

class PrioridadEnum(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"
```

**Flujo de Estados:**
```
PENDIENTE → INVESTIGACION → NOTIFICACION → FINALIZADO_ENCONTRADO
                    ↓
                    └──────────────────────→ FINALIZADO_NO_ENCONTRADO
```

**Ejemplo:**
```json
{
  "id": 1,
  "numero_oficio": "OF-2024-001",
  "buffet_id": 1,
  "investigador_id": 2,
  "estado": "investigacion",
  "prioridad": "alta",
  "fecha_ingreso": "2024-12-01",
  "fecha_limite": "2024-12-15",
  "notas_generales": "Cliente VIP - prioridad máxima"
}
```

#### 5.2.4 Vehiculo (1:1 con Oficio)

```python
class Vehiculo(Base):
    __tablename__ = "vehiculos"
    
    # Campos
    id: int                    # PK
    oficio_id: int             # FK a Oficio (UNIQUE - relación 1:1)
    patente: str               # "ABCD12"
    marca: Optional[str]       # "Toyota"
    modelo: Optional[str]      # "Corolla"
    año: Optional[int]         # 2020
    color: Optional[str]       # "Blanco"
    vin: Optional[str]         # VIN number (17 chars)
    created_at: datetime
    
    # Relaciones
    oficio: Oficio             # 1:1 - Oficio al que pertenece
```

**Validaciones:**
- `oficio_id` debe ser único (solo 1 vehículo por oficio)
- `patente` debe existir y ser válida

**Ejemplo:**
```json
{
  "id": 1,
  "oficio_id": 1,
  "patente": "ABCD12",
  "marca": "Toyota",
  "modelo": "Corolla",
  "año": 2020,
  "color": "Blanco",
  "vin": "1HGBH41JXMN109186"
}
```

#### 5.2.5 Propietario (N:1 con Oficio)

```python
class Propietario(Base):
    __tablename__ = "propietarios"
    
    # Campos
    id: int                    # PK
    oficio_id: int             # FK a Oficio
    rut: str                   # "12345678-9"
    nombre_completo: str
    email: Optional[str]
    telefono: Optional[str]
    tipo: TipoPropietarioEnum  # Tipo de propietario
    direccion_principal: Optional[str]
    notas: Optional[str]
    created_at: datetime
    
    # Relaciones
    oficio: Oficio             # N:1 - Oficio al que pertenece

# Enum
class TipoPropietarioEnum(str, Enum):
    PRINCIPAL = "principal"    # Propietario principal
    CODEUDOR = "codeudor"      # Codeudor solidario
    AVAL = "aval"              # Aval
    USUARIO = "usuario"        # Familiar que usa el vehículo
```

**¿Por qué múltiples propietarios?**
- Un vehículo puede tener propietario + codeudor + aval
- Familiar que usa el vehículo pero no es dueño
- Investigación puede revelar propietarios adicionales

**Ejemplo:**
```json
{
  "id": 1,
  "oficio_id": 1,
  "rut": "12345678-9",
  "nombre_completo": "Juan Pérez González",
  "tipo": "principal",
  "email": "juan@example.com",
  "telefono": "+56912345678"
}
```

#### 5.2.6 Direccion (N:1 con Oficio)

```python
class Direccion(Base):
    __tablename__ = "direcciones"
    
    # Campos
    id: int                      # PK
    oficio_id: int               # FK a Oficio
    direccion: str               # "Av. Principal 123"
    comuna: Optional[str]        # "Santiago"
    region: Optional[str]        # "Metropolitana"
    tipo: TipoDireccionEnum      # Tipo de dirección
    verificada: bool             # False por defecto
    fecha_verificacion: Optional[datetime]
    notas: Optional[str]
    agregada_por_id: Optional[int]  # FK a Usuario que la agregó
    created_at: datetime
    
    # Relaciones
    oficio: Oficio               # N:1 - Oficio al que pertenece

# Enum
class TipoDireccionEnum(str, Enum):
    DOMICILIO = "domicilio"      # Casa del propietario
    TRABAJO = "trabajo"          # Lugar de trabajo
    FAMILIAR = "familiar"        # Casa de familiar
```

**¿Por qué múltiples direcciones?**
- Dirección del Excel (inicial)
- Investigador encuentra direcciones adicionales (trabajo, familia)
- Se verifican en terreno

**Flujo:**
1. Excel → Dirección domicilio (no verificada)
2. Investigador llama → Agrega dirección trabajo
3. Investigador va en terreno → Verifica dirección
4. `verificada = True`, `fecha_verificacion = now()`

**Ejemplo:**
```json
{
  "id": 1,
  "oficio_id": 1,
  "direccion": "Av. Comercio 456, Piso 3, Oficina 301",
  "comuna": "Providencia",
  "region": "Metropolitana",
  "tipo": "trabajo",
  "verificada": true,
  "fecha_verificacion": "2024-12-21T14:30:00",
  "notas": "Vehículo estacionado en subterráneo",
  "agregada_por_id": 2
}
```

#### 5.2.7 Investigacion (Timeline)

```python
class Investigacion(Base):
    __tablename__ = "investigaciones"
    
    # Campos
    id: int                      # PK
    oficio_id: int               # FK a Oficio
    investigador_id: int         # FK a Usuario
    fecha_hora: datetime         # Timestamp de la actividad
    tipo_actividad: TipoActividadEnum
    descripcion: str             # Descripción de la actividad
    resultado: Optional[str]     # Resultado/conclusión
    datos_json: Optional[str]    # JSON con data adicional
    
    # Relaciones
    oficio: Oficio
    investigador: Usuario

# Enum
class TipoActividadEnum(str, Enum):
    CONSULTA_API = "consulta_api"    # Consulta a API externa
    NOTA = "nota"                    # Nota del investigador
    LLAMADA = "llamada"              # Llamada telefónica
    TERRENO = "terreno"              # Visita en terreno
```

**Ejemplo de Timeline:**
```json
[
  {
    "id": 1,
    "fecha_hora": "2024-12-01T10:00:00",
    "tipo_actividad": "consulta_api",
    "descripcion": "Consulta automática a pórticos",
    "resultado": "5 avistamientos encontrados"
  },
  {
    "id": 2,
    "fecha_hora": "2024-12-02T14:30:00",
    "tipo_actividad": "llamada",
    "descripcion": "Llamada a vecino de Av. Principal 123",
    "resultado": "Vecino confirma que vehículo estacionaba ahí hace 6 meses"
  },
  {
    "id": 3,
    "fecha_hora": "2024-12-03T11:00:00",
    "tipo_actividad": "terreno",
    "descripcion": "Visita a Av. Comercio 456 (lugar de trabajo)",
    "resultado": "Vehículo encontrado y fotografiado"
  }
]
```

#### 5.2.8 Avistamiento (Resultados de APIs)

```python
class Avistamiento(Base):
    __tablename__ = "avistamientos"
    
    # Campos
    id: int                      # PK
    oficio_id: int               # FK a Oficio
    fecha_hora: datetime         # Cuándo pasó por el pórtico
    ubicacion: Optional[str]     # "Autopista Central - Km 15"
    empresa: Optional[str]       # "Costanera Norte"
    fuente: str                  # "portico" | "multa" | "terreno"
    monto: Optional[Decimal]     # Monto del cobro (pórtico/multa)
    verificado: bool             # False por defecto
    created_at: datetime
    
    # Relaciones
    oficio: Oficio
```

**Fuentes:**
- `portico`: API de pórticos (Boostr.cl, etc.)
- `multa`: API de multas de tránsito
- `terreno`: Investigador lo registra manualmente

**Ejemplo:**
```json
{
  "id": 1,
  "oficio_id": 1,
  "fecha_hora": "2024-12-15T08:45:00",
  "ubicacion": "Autopista Central Norte, Km 15.3",
  "empresa": "Costanera Norte",
  "fuente": "portico",
  "monto": 1500.00,
  "verificado": true
}
```

#### 5.2.9 Adjunto (Fotos y Documentos)

```python
class Adjunto(Base):
    __tablename__ = "adjuntos"
    
    # Campos
    id: int                      # PK
    oficio_id: int               # FK a Oficio
    investigador_id: int         # FK a Usuario (quién lo subió)
    tipo: TipoAdjuntoEnum
    filename: str                # "foto_vehiculo_20241221_143022.jpg"
    url: str                     # Path o URL del archivo
    mime_type: Optional[str]     # "image/jpeg"
    tamaño_bytes: Optional[int]
    descripcion: Optional[str]
    fecha_subida: datetime
    metadata_json: Optional[str] # GPS coords, EXIF data, etc.
    
    # Relaciones
    oficio: Oficio
    investigador: Usuario

# Enum
class TipoAdjuntoEnum(str, Enum):
    FOTO_VEHICULO = "foto_vehiculo"    # Foto del vehículo
    DOCUMENTO = "documento"            # PDF, Word, etc.
    EVIDENCIA = "evidencia"            # Otra evidencia
```

**Storage:**
- **Local (dev):** `/app/storage/oficios/{oficio_id}/{filename}`
- **S3 (prod):** `s3://bucket/oficios/{oficio_id}/{filename}`

**Ejemplo:**
```json
{
  "id": 1,
  "oficio_id": 1,
  "investigador_id": 2,
  "tipo": "foto_vehiculo",
  "filename": "foto_vehiculo_20241221_143022.jpg",
  "url": "/storage/oficios/1/foto_vehiculo_20241221_143022.jpg",
  "mime_type": "image/jpeg",
  "tamaño_bytes": 2458624,
  "descripcion": "Vista frontal - patente visible",
  "fecha_subida": "2024-12-21T14:30:22",
  "metadata_json": "{\"gps_lat\":-33.4569,\"gps_lon\":-70.6483}"
}
```

#### 5.2.10 Notificacion (Emails)

```python
class Notificacion(Base):
    __tablename__ = "notificaciones"
    
    # Campos
    id: int                      # PK
    oficio_id: int               # FK a Oficio
    tipo: TipoNotificacionEnum
    destinatario_email: str      # Email del receptor
    asunto: str                  # Subject del email
    mensaje: str                 # Cuerpo del email (HTML)
    enviada: bool                # False hasta que se envíe
    fecha_envio: Optional[datetime]
    fecha_leida: Optional[datetime]
    respuesta: Optional[str]
    created_at: datetime
    
    # Relaciones
    oficio: Oficio

# Enum
class TipoNotificacionEnum(str, Enum):
    RECEPTOR_JUDICIAL = "receptor_judicial"  # Email a receptor
    BUFFET = "buffet"                        # Email a buffet cliente
    INTERNA = "interna"                      # Notificación interna
```

**Ejemplo:**
```json
{
  "id": 1,
  "oficio_id": 1,
  "tipo": "receptor_judicial",
  "destinatario_email": "receptor@judicial.cl",
  "asunto": "Vehículo Ubicado - Oficio OF-2024-001",
  "mensaje": "<html>...</html>",
  "enviada": true,
  "fecha_envio": "2024-12-21T15:00:00"
}
```

---

## 6. Sistema de Permisos (RBAC)

### 6.1 Matriz de Permisos

| Acción | Admin | Investigador | Cliente |
|--------|-------|--------------|---------|
| **Buffets** |
| Crear buffet | ✅ | ❌ | ❌ |
| Listar buffets | ✅ | ❌ | ❌ |
| Editar buffet | ✅ | ❌ | ❌ |
| Desactivar buffet | ✅ | ❌ | ❌ |
| **Usuarios** |
| Crear usuario | ✅ | ❌ | ❌ |
| Listar usuarios | ✅ | ❌ | ❌ |
| Editar usuario | ✅ | ❌ | ❌ |
| Cambiar rol | ✅ | ❌ | ❌ |
| Desactivar usuario | ✅ | ❌ | ❌ |
| **Oficios** |
| Crear oficio | ✅ | ✅ | ❌ |
| Listar oficios | ✅ (todos) | ✅ (todos) | ✅ (solo suyos) |
| Ver detalle | ✅ | ✅ | ✅ (solo suyos) |
| Editar oficio | ✅ | ✅ | ❌ |
| Asignar investigador | ✅ | ✅ | ❌ |
| Cambiar estado | ✅ | ✅ | ❌ |
| **Direcciones** |
| Agregar dirección | ✅ | ✅ | ❌ |
| Editar dirección | ✅ | ✅ | ❌ |
| Verificar dirección | ✅ | ✅ | ❌ |
| Eliminar dirección | ✅ | ✅ | ❌ |
| **Propietarios** |
| Agregar propietario | ✅ | ✅ | ❌ |
| Editar propietario | ✅ | ✅ | ❌ |
| Eliminar propietario | ✅ | ✅ | ❌ |
| **Adjuntos** |
| Subir adjunto | ✅ | ✅ | ❌ |
| Descargar adjunto | ✅ | ✅ | ✅ (solo suyos) |
| Eliminar adjunto | ✅ | ✅ | ❌ |
| **APIs & Tasks** |
| Consultar APIs | ✅ | ✅ | ❌ |
| Ver resultados APIs | ✅ | ✅ | ✅ (solo suyos) |
| **Notificaciones** |
| Notificar receptor | ✅ | ✅ | ❌ |
| Ver notificaciones | ✅ | ✅ | ✅ (solo suyos) |
| **Dashboard** |
| Dashboard público | ✅ | ✅ | ✅ (con token) |

### 6.2 Implementación de Permisos

#### src/core/permissions.py

```python
from fastapi import Depends, HTTPException, status
from src.infrastructure.database.models import Usuario, RolEnum
from src.core.security import get_current_active_user

async def require_admin(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Require admin role
    
    Usage:
        @router.post("/admin-only")
        async def admin_endpoint(
            current_user: Usuario = Depends(require_admin)
        ):
            pass
    """
    if current_user.rol != RolEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes. Se requiere rol de administrador."
        )
    return current_user


async def require_investigador(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Require investigador or admin role
    
    Usage:
        @router.post("/investigators-only")
        async def investigador_endpoint(
            current_user: Usuario = Depends(require_investigador)
        ):
            pass
    """
    if current_user.rol not in [RolEnum.ADMIN, RolEnum.INVESTIGADOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes. Se requiere rol de investigador o administrador."
        )
    return current_user


async def require_cliente(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Require any authenticated user (cliente, investigador, admin)
    
    Usage:
        @router.get("/protected")
        async def protected_endpoint(
            current_user: Usuario = Depends(require_cliente)
        ):
            pass
    """
    # All authenticated users can access
    return current_user


def check_oficio_access(usuario: Usuario, oficio_buffet_id: int) -> bool:
    """
    Check if user has access to specific oficio
    
    Rules:
    - Admin: access to all oficios
    - Investigador: access to all oficios
    - Cliente: only their buffet's oficios
    
    Usage:
        if not check_oficio_access(current_user, oficio.buffet_id):
            raise HTTPException(403, "No tiene acceso a este oficio")
    """
    # Admin and Investigador have access to all
    if usuario.rol in [RolEnum.ADMIN, RolEnum.INVESTIGADOR]:
        return True
    
    # Cliente only has access to their buffet's oficios
    if usuario.rol == RolEnum.CLIENTE:
        return usuario.buffet_id == oficio_buffet_id
    
    return False
```

**Uso en endpoints:**

```python
from src.core.permissions import require_admin, require_investigador, check_oficio_access

# Solo admin
@router.post("/buffets/")
async def create_buffet(
    data: BuffetCreate,
    current_user: Usuario = Depends(require_admin)  # ← Require admin
):
    # Solo admin puede crear buffets
    pass

# Admin o Investigador
@router.post("/oficios/")
async def create_oficio(
    data: OficioCreate,
    current_user: Usuario = Depends(require_investigador)  # ← Require investigador
):
    # Admin o investigador pueden crear oficios
    pass

# Cualquier usuario autenticado, pero verificar acceso
@router.get("/oficios/{id}")
async def get_oficio(
    oficio_id: int,
    current_user: Usuario = Depends(get_current_active_user)
):
    oficio = db.query(Oficio).filter(Oficio.id == oficio_id).first()
    
    # Verificar acceso
    if not check_oficio_access(current_user, oficio.buffet_id):
        raise HTTPException(403, "No tiene acceso a este oficio")
    
    return oficio
```

---

## 7. Autenticación y Seguridad

### 7.1 JWT Authentication

#### src/core/security.py

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.core.config import get_settings
from src.infrastructure.database.session import get_db
from src.infrastructure.database.models import Usuario

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dict with user data (typically {"sub": user_id})
        expires_delta: Token expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dict
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Get current authenticated user from JWT token
    
    This is the main dependency for protected endpoints
    
    Usage:
        @router.get("/protected")
        async def protected_endpoint(
            current_user: Usuario = Depends(get_current_user)
        ):
            return {"user_id": current_user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if user is None or not user.activo:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Get current active user (wrapper around get_current_user)
    
    This is an alias for get_current_user, kept for clarity
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=400, 
            detail="Usuario inactivo"
        )
    return current_user
```

### 7.2 Login Endpoint

#### src/presentation/api/v1/auth.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from src.infrastructure.database.session import get_db
from src.infrastructure.database.models import Usuario
from src.core.security import (
    verify_password,
    create_access_token,
    get_current_active_user
)
from src.core.config import get_settings
from src.presentation.schemas.schemas import (
    LoginRequest,
    LoginResponse,
    UsuarioResponse
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])
settings = get_settings()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint
    
    Returns JWT token and user info
    
    Example:
        POST /api/v1/auth/login
        {
            "email": "admin@investigaciones.cl",
            "password": "admin123"
        }

2. Backend verifica:
   - ¿Usuario existe? ✓
   - ¿Password correcto? ✓
   - ¿Usuario activo? ✓

3. Backend genera JWT:
   {
     "sub": 1,           # user_id
     "exp": 1735689600   # expiration timestamp
   }

4. Backend responde:
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "user": {
       "id": 1,
       "email": "admin@investigaciones.cl",
       "nombre": "Admin",
       "rol": "admin"
     }
   }

5. Cliente guarda token en localStorage/cookie

6. Para requests protegidos:
   GET /api/v1/oficios/
   Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

7. Backend valida token:
   - Decodifica JWT
   - Extrae user_id
   - Busca usuario en DB
   - Verifica que esté activo
   - Inyecta usuario en endpoint
```

---

**FIN PARTE 2/4**

Continuaré con la Parte 3 que incluirá:
- Configuración completa (config.py)
- Endpoints API detallados
- Schemas Pydantic completos
- Ejemplos de requests/responses

¿Continúo con la Parte 3?
        
    Response:
        {
            "access_token": "eyJ...",
            "token_type": "bearer",
            "user": { ... }
        }
    """
    # Find user by email
    user = db.query(Usuario).filter(Usuario.email == request.email).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UsuarioResponse.model_validate(user)
    )


@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Get current user information
    
    Requires authentication (Bearer token)
    
    Example:
        GET /api/v1/auth/me
        Headers: Authorization: Bearer <token>
    """
    return UsuarioResponse.model_validate(current_user)
```

### 7.3 Schemas de Autenticación

```python
# src/presentation/schemas/schemas.py

from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """Login request payload"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    """Login response with user info"""
    access_token: str
    token_type: str
    user: UsuarioResponse  # Defined elsewhere
```

### 7.4 Flujo de Autenticación

```
1. Cliente → POST /api/v1/auth/login
   {
     "email": "admin@investigaciones.cl",
     "password": "admin123"
   