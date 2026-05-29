# ETAPA 1: Base comune para todas las etapas
FROM python:3.12-slim AS base

# Configuración defensiva de Python en contenedores
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=.

WORKDIR /app


# ETAPA 2: Builder
FROM base AS builder
# Instalamos herramientas de sistema necesarias solo para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ETAPA 3: Testing / SUT
FROM base AS development
# Copiamos las dependencias compiladas desde el builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
# Instalamos dependencias exclusivas de pruebas
RUN pip install --no-cache-dir pytest pytest-env
COPY src/ ./src
COPY tests/ ./tests
COPY pyproject.toml .


# ETAPA 4: Producción
FROM base AS production
# Copiamos únicamente las dependencias de producción limpias
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
# Copiamos solo el código de ejecucion
COPY src/ ./src
CMD ["python3", "-m", "src.pipeline"]