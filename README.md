# FastDelivery — Monorepo

## Estrutura

```
server/     → Backend (FastAPI + PortunusDB) — API de delivery
```

## Backend

```bash
cd server
cp .env.example .env   # configurar
python -m uvicorn src.main:create_app --factory --reload
```
