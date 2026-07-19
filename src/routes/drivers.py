# Rotas do entregador - esqueleto
from loguru import logger


def get_profile():
    logger.info("rota: perfil do entregador")
    return {}


def update_profile():
    logger.info("rota: atualizar perfil")
    return {}


def go_online():
    logger.info("rota: ficar online")
    return {}


def go_offline():
    logger.info("rota: ficar offline")
    return {}


def get_location():
    return {}


def update_location():
    logger.info("rota: atualizar localização")
    return {}


def list_available():
    return {}


def accept_order():
    logger.info("rota: aceitar ordem")
    return {}


def reject_order():
    logger.info("rota: recusar ordem")
    return {}


def mark_collected():
    logger.info("rota: marcar coletado")
    return {}


def mark_in_delivery():
    logger.info("rota: saiu para entrega")
    return {}


def mark_delivered():
    logger.info("rota: marcar entregue")
    return {}


def get_current():
    return {}


def get_history():
    return {}


def get_balance():
    return {}


def saque():
    logger.info("rota: saque")
    return {}


def get_pay_history():
    return {}
