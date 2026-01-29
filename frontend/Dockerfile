# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependências Python do builder
COPY --from=builder /root/.local /root/.local

# Copiar código da aplicação
COPY chainlit_app.py .
COPY auth_handler.py .
COPY admin_interface.py .
COPY chat_interface.py .
COPY .chainlit/ ./.chainlit/
COPY .env.example .env

# Definir variáveis de ambiente
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501 || exit 1

# Comando padrão
CMD ["chainlit", "run", "chainlit_app.py", "--host", "0.0.0.0", "--port", "8501"]
