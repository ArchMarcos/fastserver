#!/usr/bin/env python3
"""Cria o banco de dados e todas as tabelas do projeto.

Uso:
    python setup_db.py
    python setup_db.py --reset   # recria tudo (apaga dados)

Idempotente: não recria tabelas que já existem (a menos que --reset).
"""

import argparse
import sys

from portunus import Client
from loguru import logger

from src.infra.config import settings

DB_NAME = settings.DATABASE_NAME

TABLES = [
    "clients",
    "merchants",
    "drivers",
    "tokens",
    "products",
    "carts",
    "sub_ordens",
    "ordens",
    "transferencias",
    "recargas",
    "comprovantes",
    "email_confirmations",
    "driver_history",
    "coupons",
    "ratings",
    "favorites",
]


def main():
    parser = argparse.ArgumentParser(description="Cria banco e tabelas do FastDelivery")
    parser.add_argument("--reset", action="store_true", help="Recria tudo (⚠️ apaga dados)")
    args = parser.parse_args()

    # ── Conectar ──
    logger.info("Conectando ao PortunusDB em {host}", host=settings.DATABASE_HOST)

    try:
        db = Client(
            settings.DATABASE_HOST,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
        )
    except Exception as e:
        logger.error("Falha ao conectar ao PortunusDB: {err}", err=e)
        logger.error("Verifique se o servidor está rodando: portunusd --port 3100")
        sys.exit(1)

    # ── Reset ──
    if args.reset:
        dbs = db.list_databases()
        if DB_NAME in dbs:
            logger.warning("🗑️  Removendo banco '{db}'...", db=DB_NAME)
            try:
                db.delete_database(DB_NAME)
            except Exception:
                logger.warning("Falha ao deletar banco (pode não existir)")

    # ── Database ──
    dbs = db.list_databases()
    if DB_NAME in dbs:
        logger.info("Banco '{db}' já existe", db=DB_NAME)
    else:
        db.create_database(DB_NAME)
        logger.info("✅ Banco '{db}' criado", db=DB_NAME)

    # ── Tables ──
    db.use(DB_NAME)
    existing = set(db.list_tables())

    created = 0
    skipped = 0

    for table in TABLES:
        if table in existing:
            logger.debug("  ⏭️  {table} (já existe)", table=table)
            skipped += 1
        else:
            db.create_table(table)
            logger.info("  ✅ {table} criada", table=table)
            created += 1

    # ── Resumo ──
    total = len(TABLES)
    logger.info(
        "Setup concluído — {created} criadas, {skipped} existentes, {total} total",
        created=created,
        skipped=skipped,
        total=total,
    )

    if created == 0 and not args.reset:
        logger.info("💡 Use --reset para recriar tudo")


if __name__ == "__main__":
    main()
