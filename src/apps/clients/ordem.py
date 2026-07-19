# Ordem do cliente - esqueleto
from src.database.database import ordens, sub_ordens
from loguru import logger

CANCELAVEIS = ["pendente", "aceito", "preparando", "pronto", "esperando_entregador"]


def create_ordem(client_id, entregar_em, obs="", payment_method="saldo"):
    logger.info("criar ordem: {client_id} método: {payment_method}", client_id=client_id, payment_method=payment_method)
    return "ordem criada"


def list_ordens(client_id):
    return []


def list_ordens_active(client_id):
    return []


def list_ordens_history(client_id):
    return []


def get_ordem(ordem_id):
    return {}


def cancel_ordem(ordem_id):
    ordem = get_ordem(ordem_id)
    if ordem.get("status") not in CANCELAVEIS:
        logger.warning("cancelamento bloqueado: {ordem_id}", ordem_id=ordem_id)
        return "não é possível cancelar após coleta do entregador"
    logger.info("ordem cancelada: {ordem_id}", ordem_id=ordem_id)
    return "ordem cancelada"


def get_sub_ordens(ordem_id):
    return []


def get_sub_ordem(sub_ordem_id):
    return {}


def cancel_sub_ordem(sub_ordem_id):
    sub = get_sub_ordem(sub_ordem_id)
    if sub.get("status") not in CANCELAVEIS:
        logger.warning("cancelamento de sub-ordem bloqueado: {sub_ordem_id}", sub_ordem_id=sub_ordem_id)
        return "não é possível cancelar sub-ordem após coleta"
    logger.info("sub-ordem cancelada: {sub_ordem_id}", sub_ordem_id=sub_ordem_id)
    return "sub-ordem cancelada"


def rate_ordem(ordem_id, score, comment=""):
    logger.info("avaliar ordem: {ordem_id} nota: {score}", ordem_id=ordem_id, score=score)
    return "avaliação registrada"
