# Rotas do merchant - esqueleto
from loguru import logger


def get_profile():
    logger.info("rota: perfil do merchant")
    return {}


def update_profile():
    logger.info("rota: atualizar perfil")
    return {}


def toggle_open():
    logger.info("rota: alternar abertura")
    return {}


def list_products():
    return {}


def create_product():
    logger.info("rota: criar produto")
    return {}


def update_product():
    logger.info("rota: atualizar produto")
    return {}


def remove_product():
    logger.info("rota: remover produto")
    return {}


def list_ordens():
    return {}


def list_pending():
    return {}


def accept_sub_ordem():
    logger.info("rota: aceitar sub-ordem")
    return {}


def refuse_sub_ordem():
    logger.info("rota: recusar sub-ordem")
    return {}


def start_preparing():
    logger.info("rota: iniciar preparo")
    return {}


def mark_ready():
    logger.info("rota: marcar pronto")
    return {}


def waiting_driver():
    logger.info("rota: aguardando entregador")
    return {}


def get_balance():
    return {}


def saque():
    logger.info("rota: saque")
    return {}


def get_history():
    return {}
