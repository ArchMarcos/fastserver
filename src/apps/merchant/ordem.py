# Ordem do merchant - esqueleto
from src.database.database import ordens, sub_ordens
from loguru import logger


def list_pending(merchant_id):
    return []


def list_all(merchant_id):
    return []


def list_active(merchant_id):
    return []


def list_history(merchant_id):
    return []


def get_sub_ordem(sub_ordem_id):
    return {}


def accept(sub_ordem_id):
    logger.info("sub-ordem aceita: {sub_ordem_id}", sub_ordem_id=sub_ordem_id)
    return "sub-ordem aceita"


def refuse(sub_ordem_id):
    logger.info("sub-ordem recusada: {sub_ordem_id}", sub_ordem_id=sub_ordem_id)
    return "sub-ordem recusada"


def start_preparing(sub_ordem_id):
    logger.info("preparo iniciado: {sub_ordem_id}", sub_ordem_id=sub_ordem_id)
    return "preparo iniciado"


def mark_ready(sub_ordem_id):
    logger.info("pronto para coleta: {sub_ordem_id}", sub_ordem_id=sub_ordem_id)
    return "pronto para coleta"


def waiting_driver(sub_ordem_id):
    logger.info("esperando entregador: {sub_ordem_id}", sub_ordem_id=sub_ordem_id)
    return "esperando entregador"


def mark_collected(sub_ordem_id):
    logger.info("coletado pelo entregador: {sub_ordem_id}", sub_ordem_id=sub_ordem_id)
    return "coletado pelo entregador"


def list_ordens(merchant_id):
    return []


def get_ordem(ordem_id):
    return {}


def calc_earnings(merchant_id):
    return 0.0
