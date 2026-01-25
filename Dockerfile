# Dockerfile para despliegue
# Usa Python 3.12 explícitamente para evitar problemas de compatibilidad

FROM python:3.12.7-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copiar código
COPY . .

# Script de inicio que ejecuta migraciones y luego inicia el servidor
COPY docker-entrypoint.sh /docker-entrypoint.sh

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod +x /docker-entrypoint.sh
USER appuser

# Exponer puerto
EXPOSE 8000

# Comando por defecto
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

