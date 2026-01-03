# PARTE 4: CELERY TASKS, TESTING Y DEPLOYMENT

## 9. Celery Tasks (Tareas Asíncronas)

### 9.1 Configuración de Celery

**src/tasks/celery_app.py:**
```python
from celery import Celery
from celery.schedules import crontab
from src.core.config import get_settings

settings = get_settings()

# Crear app de Celery
celery_app = Celery(
    "investigaciones",
    broker=settings.REDIS_URL,        # Redis como message broker
    backend=settings.REDIS_URL,       # Redis para guardar resultados
    include=[
        "src.tasks.api_consultas",    # Importar tasks
        "src.tasks.notificaciones"
    ]
)

# Configuración
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Santiago",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,              # 5 minutos máximo
    task_soft_time_limit=240,         # 4 minutos soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Tareas programadas (Celery Beat)
celery_app.conf.beat_schedule = {
    "check-pending-oficios": {
        "task": "src.tasks.api_consultas.check_pending_oficios",
        "schedule": crontab(minute=0),  # Cada hora
    },
}
```

### 9.2 Task: Consultar APIs de Pórticos

**src/tasks/api_consultas.py:**
```python
from celery import Task
from src.tasks.celery_app import celery_app
from src.infrastructure.database.session import SessionLocal
from src.infrastructure.database.models import (
    Oficio, Vehiculo, Avistamiento, Investigacion,
    EstadoOficioEnum, TipoActividadEnum
)
from src.core.config import get_settings
import httpx
from datetime import datetime
import json

settings = get_settings()


class DatabaseTask(Task):
    """Base task con database session"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(bind=True, base=DatabaseTask, max_retries=3)
def consultar_porticos_vehiculo(self, oficio_id: int):
    """
    Consultar pórticos para un vehículo
    
    Args:
        oficio_id: ID del oficio a consultar
    
    Returns:
        Dict con status y resultados
    
    Retry:
        3 reintentos con backoff exponencial
    """
    try:
        # 1. Obtener oficio y vehículo
        oficio = self.db.query(Oficio).filter(Oficio.id == oficio_id).first()
        if not oficio or not oficio.vehiculo:
            return {"error": "Oficio o vehículo no encontrado"}
        
        vehiculo = oficio.vehiculo
        
        # 2. Registrar actividad en timeline
        investigacion = Investigacion(
            oficio_id=oficio_id,
            investigador_id=oficio.investigador_id or 1,
            tipo_actividad=TipoActividadEnum.CONSULTA_API,
            descripcion=f"Consulta automática a API de pórticos para patente {vehiculo.patente}",
            fecha_hora=datetime.utcnow()
        )
        self.db.add(investigacion)
        
        # 3. Llamar API externa
        if settings.BOOSTR_API_KEY and settings.BOOSTR_API_URL:
            try:
                response = httpx.get(
                    f"{settings.BOOSTR_API_URL}/porticos/{vehiculo.patente}",
                    headers={"Authorization": f"Bearer {settings.BOOSTR_API_KEY}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 4. Guardar avistamientos
                    avistamientos_count = 0
                    for item in data.get("avistamientos", []):
                        avistamiento = Avistamiento(
                            oficio_id=oficio_id,
                            fecha_hora=datetime.fromisoformat(item["fecha_hora"]),
                            ubicacion=item.get("ubicacion"),
                            empresa=item.get("empresa"),
                            fuente="portico",
                            monto=item.get("monto")
                        )
                        self.db.add(avistamiento)
                        avistamientos_count += 1
                    
                    investigacion.resultado = f"Se encontraron {avistamientos_count} avistamientos"
                    investigacion.datos_json = json.dumps(data)
                    
            except Exception as e:
                investigacion.resultado = f"Error en consulta API: {str(e)}"
        else:
            # Mock data para desarrollo
            investigacion.resultado = "API no configurada - datos de prueba"
            investigacion.datos_json = json.dumps({
                "avistamientos": [
                    {
                        "fecha_hora": datetime.utcnow().isoformat(),
                        "ubicacion": "Autopista Central - Km 15",
                        "empresa": "Costanera Norte",
                        "monto": 1500
                    }
                ]
            })
        
        # 5. Guardar todo
        self.db.commit()
        
        return {
            "oficio_id": oficio_id,
            "patente": vehiculo.patente,
            "status": "completed"
        }
        
    except Exception as exc:
        self.db.rollback()
        # Retry con backoff exponencial: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, base=DatabaseTask)
def check_pending_oficios(self):
    """
    Tarea programada: revisar oficios pendientes
    
    Se ejecuta cada hora (configurado en beat_schedule)
    
    Consulta APIs para oficios que:
    - Están en estado INVESTIGACION
    - No tienen consulta en últimas 24 horas
    """
    oficios = self.db.query(Oficio).filter(
        Oficio.estado == EstadoOficioEnum.INVESTIGACION
    ).limit(10).all()
    
    for oficio in oficios:
        # Verificar última consulta
        last_check = self.db.query(Investigacion).filter(
            Investigacion.oficio_id == oficio.id,
            Investigacion.tipo_actividad == TipoActividadEnum.CONSULTA_API
        ).order_by(Investigacion.fecha_hora.desc()).first()
        
        # Si no hay consulta o fue hace más de 24 horas
        if not last_check or (datetime.utcnow() - last_check.fecha_hora).days >= 1:
            # Encolar consulta
            consultar_porticos_vehiculo.delay(oficio.id)
    
    return {"processed": len(oficios)}
```

### 9.3 Task: Notificar Receptor Judicial

**src/tasks/notificaciones.py:**
```python
from celery import Task
from src.tasks.celery_app import celery_app
from src.infrastructure.database.session import SessionLocal
from src.infrastructure.database.models import (
    Oficio, Notificacion, Adjunto, TipoNotificacionEnum
)
from src.core.config import get_settings
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from pathlib import Path

settings = get_settings()


class DatabaseTask(Task):
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(bind=True, base=DatabaseTask, max_retries=3)
def notificar_receptor_judicial(
    self,
    oficio_id: int,
    receptor_email: str,
    mensaje_adicional: str = "",
    adjuntos_ids: list = None
):
    """
    Enviar notificación por email al receptor judicial
    
    Args:
        oficio_id: ID del oficio
        receptor_email: Email del receptor
        mensaje_adicional: Mensaje adicional del investigador
        adjuntos_ids: Lista de IDs de adjuntos (fotos)
    
    Returns:
        Dict con status del envío
    """
    try:
        # 1. Obtener oficio
        oficio = self.db.query(Oficio).filter(Oficio.id == oficio_id).first()
        if not oficio:
            return {"error": "Oficio no encontrado"}
        
        # 2. Crear registro de notificación
        notificacion = Notificacion(
            oficio_id=oficio_id,
            tipo=TipoNotificacionEnum.RECEPTOR_JUDICIAL,
            destinatario_email=receptor_email,
            asunto=f"Vehículo Ubicado - Oficio {oficio.numero_oficio}",
            mensaje=""
        )
        
        # 3. Construir email HTML
        vehiculo = oficio.vehiculo
        direcciones_verificadas = [d for d in oficio.direcciones if d.verificada]
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Notificación de Vehículo Ubicado</h2>
            
            <h3>Datos del Oficio:</h3>
            <ul>
                <li><strong>Número:</strong> {oficio.numero_oficio}</li>
                <li><strong>Fecha:</strong> {oficio.fecha_ingreso.strftime('%d/%m/%Y')}</li>
                <li><strong>Buffet:</strong> {oficio.buffet.nombre}</li>
            </ul>
            
            <h3>Datos del Vehículo:</h3>
            <ul>
                <li><strong>Patente:</strong> {vehiculo.patente}</li>
                <li><strong>Marca/Modelo:</strong> {vehiculo.marca} {vehiculo.modelo}</li>
                <li><strong>Año:</strong> {vehiculo.año}</li>
                <li><strong>Color:</strong> {vehiculo.color}</li>
            </ul>
        """
        
        # Agregar direcciones verificadas
        if direcciones_verificadas:
            html_body += "<h3>Ubicación Verificada:</h3><ul>"
            for direccion in direcciones_verificadas:
                html_body += f"""
                <li>
                    <strong>{direccion.direccion}</strong>, {direccion.comuna}<br>
                    <em>Verificada el {direccion.fecha_verificacion.strftime('%d/%m/%Y %H:%M')}</em><br>
                    {direccion.notas or ''}
                </li>
                """
            html_body += "</ul>"
        
        # Mensaje adicional
        if mensaje_adicional:
            html_body += f"""
            <h3>Observaciones:</h3>
            <p>{mensaje_adicional}</p>
            """
        
        html_body += """
            <hr>
            <p style="color: #666; font-size: 12px;">
                Este es un mensaje automático del Sistema de Investigaciones Vehiculares.<br>
                Por favor no responda a este correo.
            </p>
        </body>
        </html>
        """
        
        # 4. Crear mensaje MIME
        msg = MIMEMultipart('related')
        msg['Subject'] = notificacion.asunto
        msg['From'] = settings.SMTP_FROM
        msg['To'] = receptor_email
        msg.attach(MIMEText(html_body, 'html'))
        
        # 5. Adjuntar fotos
        if adjuntos_ids:
            adjuntos = self.db.query(Adjunto).filter(
                Adjunto.id.in_(adjuntos_ids)
            ).all()
            
            for adjunto in adjuntos:
                try:
                    file_path = Path(adjunto.url)
                    if file_path.exists():
                        with open(file_path, 'rb') as f:
                            img_data = f.read()
                        
                        img = MIMEImage(img_data)
                        img.add_header(
                            'Content-Disposition', 
                            'attachment', 
                            filename=adjunto.filename
                        )
                        msg.attach(img)
                except Exception as e:
                    print(f"Error adjuntando {adjunto.filename}: {e}")
        
        # 6. Enviar email
        notificacion.mensaje = html_body
        
        if settings.SMTP_HOST and settings.SMTP_USER:
            try:
                import asyncio
                
                async def send_email():
                    await aiosmtplib.send(
                        msg,
                        hostname=settings.SMTP_HOST,
                        port=settings.SMTP_PORT,
                        username=settings.SMTP_USER,
                        password=settings.SMTP_PASSWORD,
                        use_tls=True
                    )
                
                asyncio.run(send_email())
                
                notificacion.enviada = True
                notificacion.fecha_envio = datetime.utcnow()
                
            except Exception as e:
                notificacion.enviada = False
                print(f"Error enviando email: {e}")
        else:
            # Modo desarrollo - simular envío
            notificacion.enviada = True
            notificacion.fecha_envio = datetime.utcnow()
            print(f"[MOCK] Email enviado a {receptor_email}")
        
        # 7. Guardar notificación
        self.db.add(notificacion)
        self.db.commit()
        
        return {
            "oficio_id": oficio_id,
            "receptor_email": receptor_email,
            "enviada": notificacion.enviada,
            "notificacion_id": notificacion.id
        }
        
    except Exception as exc:
        self.db.rollback()
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### 9.4 Uso de Tasks desde API

```python
# En un endpoint de FastAPI
from src.tasks.api_consultas import consultar_porticos_vehiculo
from src.tasks.notificaciones import notificar_receptor_judicial

@router.post("/oficios/{id}/consultar-apis")
async def consultar_apis(
    oficio_id: int,
    current_user: Usuario = Depends(require_investigador)
):
    # Encolar tarea (NO bloqueante)
    task = consultar_porticos_vehiculo.delay(oficio_id)
    
    return {
        "message": "Consulta encolada",
        "task_id": task.id,
        "status": "pending"
    }


@router.post("/oficios/{id}/notificar-receptor")
async def notificar_receptor(
    oficio_id: int,
    request: NotificarReceptorRequest,
    current_user: Usuario = Depends(require_investigador)
):
    # Encolar notificación
    task = notificar_receptor_judicial.delay(
        oficio_id=oficio_id,
        receptor_email=request.receptor_email,
        mensaje_adicional=request.mensaje_adicional or "",
        adjuntos_ids=request.adjuntos_ids
    )
    
    return {
        "message": "Notificación encolada",
        "task_id": task.id
    }
```

### 9.5 Monitoreo con Flower

```bash
# Acceder a Flower
http://localhost:5555

# Características:
- Ver tareas activas
- Ver historial de ejecuciones
- Ver resultados de tareas
- Ver workers status
- Ver estadísticas
- Reintentar tareas fallidas
```

---

## 10. Testing

### 10.1 Configuración de Tests

**tests/conftest.py:**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.infrastructure.database.models import Base
from src.infrastructure.database.session import get_db
from src.core.security import get_password_hash
from src.infrastructure.database.models import Usuario, Buffet, RolEnum

# Database de prueba (SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Fixture de base de datos"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Fixture de cliente HTTP"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def admin_user(db):
    """Fixture de usuario admin"""
    user = Usuario(
        email="admin@test.com",
        nombre="Admin Test",
        password_hash=get_password_hash("admin123"),
        rol=RolEnum.ADMIN,
        activo=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_buffet(db):
    """Fixture de buffet de prueba"""
    buffet = Buffet(
        nombre="Buffet Test",
        rut="76.123.456-7",
        email_principal="test@buffet.cl",
        token_tablero="test_token_123",
        activo=True
    )
    db.add(buffet)
    db.commit()
    db.refresh(buffet)
    return buffet
```

### 10.2 Test de Autenticación

**tests/test_auth.py:**
```python
def test_login_success(client, admin_user):
    """Test login exitoso"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test.com",
            "password": "admin123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@test.com"


def test_login_wrong_password(client, admin_user):
    """Test login con contraseña incorrecta"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test.com",
            "password": "wrong_password"
        }
    )
    
    assert response.status_code == 401
    assert "incorrectos" in response.json()["detail"].lower()


def test_login_inactive_user(client, db, admin_user):
    """Test login con usuario inactivo"""
    admin_user.activo = False
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test.com",
            "password": "admin123"
        }
    )
    
    assert response.status_code == 403
    assert "inactivo" in response.json()["detail"].lower()


def test_get_current_user(client, admin_user):
    """Test obtener usuario actual"""
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["rol"] == "admin"
```

### 10.3 Test de Buffets

**tests/test_buffets.py:**
```python
def test_create_buffet_as_admin(client, admin_user):
    """Test crear buffet como admin"""
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Create buffet
    response = client.post(
        "/api/v1/buffets/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nombre": "Nuevo Buffet",
            "rut": "77.234.567-8",
            "email_principal": "nuevo@buffet.cl",
            "telefono": "+56912345678"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Nuevo Buffet"
    assert data["rut"] == "77.234.567-8"
    assert "token_tablero" in data
    assert data["activo"] is True


def test_create_buffet_duplicate_rut(client, admin_user, test_buffet):
    """Test crear buffet con RUT duplicado"""
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/api/v1/buffets/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nombre": "Otro Buffet",
            "rut": test_buffet.rut,  # RUT duplicado
            "email_principal": "otro@buffet.cl"
        }
    )
    
    assert response.status_code == 400
    assert "ya existe" in response.json()["detail"].lower()
```

### 10.4 Ejecutar Tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=src tests/

# Tests específicos
pytest tests/test_auth.py

# Verbose
pytest -v

# Stop at first failure
pytest -x
```

---

## 11. Deployment

### 11.1 Variables de Entorno (Producción)

```bash
# .env.production

# Environment
ENVIRONMENT=production

# Security
SECRET_KEY=<genera-secreto-de-32-chars-minimo>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (PostgreSQL en producción)
DATABASE_URL=postgresql://user:pass@db-host:5432/investigaciones_prod

# Redis
REDIS_URL=redis://redis-host:6379/0

# CORS
BACKEND_CORS_ORIGINS=["https://tudominio.com","https://app.tudominio.com"]

# Email (Usar servicio real)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
SMTP_FROM=noreply@tudominio.com

# Storage (AWS S3)
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=<aws-key>
AWS_SECRET_ACCESS_KEY=<aws-secret>
AWS_REGION=us-east-1
S3_BUCKET_NAME=investigaciones-prod

# External APIs
BOOSTR_API_URL=https://api.boostr.cl
BOOSTR_API_KEY=<real-api-key>

# Monitoring
SENTRY_DSN=<sentry-dsn>
```

### 11.2 Docker Compose (Producción)

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  api:
    image: investigaciones-api:latest
    restart: always
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery_worker:
    image: investigaciones-api:latest
    restart: always
    command: celery -A src.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis

  celery_beat:
    image: investigaciones-api:latest
    restart: always
    command: celery -A src.tasks.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - redis

  db:
    image: postgres:16-alpine
    restart: always
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 11.3 Deploy en Railway/Render

```bash
# 1. Build Docker image
docker build -t investigaciones-api:latest .

# 2. Push to registry
docker tag investigaciones-api:latest registry.railway.app/investigaciones-api
docker push registry.railway.app/investigaciones-api

# 3. Railway detecta y despliega automáticamente
# O usar CLI:
railway up
```

### 11.4 Migraciones en Producción

```bash
# 1. Aplicar migraciones
alembic upgrade head

# 2. Crear migración nueva
alembic revision --autogenerate -m "Add new table"

# 3. Rollback
alembic downgrade -1
```

---

## 12. Comandos Útiles (Makefile)

```bash
# Desarrollo
make dev          # Levantar desarrollo (Docker)
make logs         # Ver logs de API
make logs-celery  # Ver logs de Celery
make shell        # Shell del contenedor
make db-shell     # PostgreSQL shell

# Base de Datos
make init-db      # Inicializar con datos de prueba
make migration    # Crear migración
make migrate      # Aplicar migraciones
make reset-db     # Resetear DB (CUIDADO)

# Code Quality
make format       # Black formatter
make lint         # Ruff linter
make type-check   # Mypy type checker
make test         # Run tests
make test-cov     # Tests con coverage

# Producción
make prod         # Levantar producción
make backup-db    # Backup de BD
make restore-db   # Restaurar BD
```

---

## 13. Checklist de Implementación para Cursor

### Fase 1: Setup Inicial
- [ ] Crear estructura de carpetas
- [ ] Copiar todos los archivos de artifacts
- [ ] Crear `.env` desde `.env.example`
- [ ] Verificar que todos los `__init__.py` existen
- [ ] `pip install -r requirements.txt`

### Fase 2: Database
- [ ] `docker-compose up -d db redis`
- [ ] Esperar 10 segundos
- [ ] `python scripts/init_db.py`
- [ ] Verificar tablas creadas en PostgreSQL

### Fase 3: API
- [ ] `docker-compose up -d api`
- [ ] Verificar logs: `docker-compose logs -f api`
- [ ] Acceder a docs: http://localhost:8000/docs
- [ ] Probar login con credenciales de prueba

### Fase 4: Celery
- [ ] `docker-compose up -d celery_worker celery_beat`
- [ ] Verificar workers: http://localhost:5555
- [ ] Probar task de prueba

### Fase 5: Tests
- [ ] Crear `tests/conftest.py`
- [ ] Implementar tests básicos
- [ ] `pytest` para ejecutar
- [ ] Coverage > 70%

### Fase 6: Frontend Integration
- [ ] En Next.js: `USE_MOCK_DATA = false`
- [ ] Configurar `NEXT_PUBLIC_API_URL`
- [ ] Probar login desde frontend
- [ ] Verificar CORS configurado

### Fase 7: Features Faltantes
- [ ] Endpoint de subida de adjuntos
- [ ] Dashboard público por token
- [ ] Tablero Kanban GET endpoint
- [ ] WebSockets (opcional)

### Fase 8: Production Ready
- [ ] Configurar variables de producción
- [ ] Setup S3 para storage
- [ ] Configurar SMTP real
- [ ] Setup Sentry monitoring
- [ ] Deploy en Railway/Render
- [ ] Aplicar migraciones en prod
- [ ] Smoke tests en producción

---

## 14. Tips para Cursor AI

### Prompt Templates

**Para crear un nuevo endpoint:**
```
Crea un endpoint POST /api/v1/[recurso] siguiendo estos patrones:
1. Usar dependencies de src/core/permissions.py
2. Validar con Pydantic schemas
3. SQLAlchemy para DB operations
4. Retornar response model
5. Manejo de errores con HTTPException

Sigue el patrón de src/presentation/api