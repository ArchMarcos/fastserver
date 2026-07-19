#!/usr/bin/env python3
"""Cria o banco de dados e todas as tabelas do projeto.

Uso:
    python setup_db.py

Idempotente: não recria se já existir.
"""

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
    logger.info("conectando ao servidor {host}", host=settings.DATABASE_HOST)
    db = Client(
        settings.DATABASE_HOST,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
    )

    # --- Database ---
    dbs = db.list_databases()
    if DB_NAME in dbs:
        logger.info("banco '{db}' já existe", db=DB_NAME)
    else:
        db.create_database(DB_NAME)
        logger.info("banco '{db}' criado", db=DB_NAME)

    # --- Tables ---
    db.use(DB_NAME)
    existing = db.list_tables()

    for table in TABLES:
        if table in existing:
            logger.info("tabela '{table}' já existe", table=table)
        else:
            db.create_table(table)
            logger.info("tabela '{table}' criada", table=table)

    logger.info("setup concluído — {total} tabelas disponíveis", total=len(TABLES))


if __name__ == "__main__":
    main()
