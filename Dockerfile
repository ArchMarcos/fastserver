# ── FastDelivery Docker image ──
FROM python:3.11-slim

LABEL org.opencontainers.image.title="FastDelivery"
LABEL org.opencontainers.image.description="API de delivery — FastAPI + PortunusDB"

WORKDIR /app

# Dependências do sistema
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar SDK Portunus (do vendor local)
COPY vendor/ ./vendor/
RUN pip install --no-cache-dir ./vendor/

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código da aplicação
COPY src/ ./src/
COPY setup_db.py .

# Entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3101/health || exit 1

EXPOSE 3101

ENTRYPOINT ["/docker-entrypoint.sh"]
