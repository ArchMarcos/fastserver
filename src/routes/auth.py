# Rotas de auth - esqueleto
from loguru import logger


def register_client():
    logger.info("rota: cadastrar cliente")
    return {}


def register_merchant():
    logger.info("rota: cadastrar merchant")
    return {}


def register_driver():
    logger.info("rota: cadastrar entregador")
    return {}


def login():
    logger.info("rota: login")
    return {}


def confirm_email():
    logger.info("rota: confirmar e-mail")
    return {}


def resend_confirmation():
    logger.info("rota: reenviar confirmação")
    return {}


def logout():
    logger.info("rota: logout")
    return {}
