# Rotas do cliente - esqueleto
from loguru import logger


def get_profile():
    logger.info("rota: perfil do cliente")
    return {}


def update_profile():
    logger.info("rota: atualizar perfil")
    return {}


def get_cart():
    return {}


def add_to_cart():
    logger.info("rota: adicionar ao carrinho")
    return {}


def remove_from_cart():
    logger.info("rota: remover do carrinho")
    return {}


def search_vitrine():
    return {}


def list_by_category():
    return {}


def list_by_merchant():
    return {}


def list_ordens():
    return {}


def create_ordem():
    logger.info("rota: criar ordem")
    return {}


def get_ordem():
    return {}


def cancel_ordem():
    logger.info("rota: cancelar ordem")
    return {}


def rate_ordem():
    logger.info("rota: avaliar ordem")
    return {}


def get_favorites():
    return {}


def add_favorite():
    logger.info("rota: adicionar favorito")
    return {}


def remove_favorite():
    logger.info("rota: remover favorito")
    return {}


def get_balance():
    return {}


def recharge():
    logger.info("rota: recarga")
    return {}


def get_history():
    return {}


def get_comprovantes():
    return {}


def get_notifications():
    return {}
