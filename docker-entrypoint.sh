#!/bin/bash
set -e

echo "🚀 FastDelivery — iniciando container"
echo "   DB: ${DATABASE_HOST:-http://localhost:3100}"

# Aguardar PortunusDB (timeout 30s)
echo "⏳ Aguardando PortunusDB..."
for i in $(seq 1 30); do
    if curl -s "${DATABASE_HOST:-http://localhost:3100}" > /dev/null 2>&1; then
        echo "✅ PortunusDB respondeu após ${i}s"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PortunusDB não respondeu em 30s. Verifique DATABASE_HOST."
        exit 1
    fi
    sleep 1
done

# Setup do banco (idempotente)
echo "🗄️  Verificando banco e tabelas..."
python setup_db.py

# Iniciar API
echo "🌐 Iniciando FastAPI em 0.0.0.0:3101"
exec python -m uvicorn src.main:create_app --factory --host 0.0.0.0 --port 3101
