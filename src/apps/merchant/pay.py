# Pagamento do merchant - esqueleto
from src.database.database import transferencias, comprovantes
from loguru import logger


def saque(merchant_id):
    logger.info("saque do merchant: {merchant_id}", merchant_id=merchant_id)
    return "pix enviado"


def get_balance(merchant_id):
    return 0.0


def get_history(merchant_id):
    return []


def calc_liquid(merchant_id):
    return 0.0


def get_comprovante_by_transfer(transferencia_id):
    return {}


def list_comprovantes(merchant_id):
    return []
