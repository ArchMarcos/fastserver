# Auth middleware - esqueleto
from src.utils.tokens import verify_token, decode_token
from loguru import logger


def auth_required(token):
    logger.info("autenticação necessária")
    return {}


def client_required(token):
    logger.info("cliente necessário")
    return {}


def merchant_required(token):
    logger.info("merchant necessário")
    return {}


def driver_required(token):
    logger.info("entregador necessário")
    return {}


def admin_required(token):
    logger.info("admin necessário")
    return {}
