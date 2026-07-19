# Pagamento do entregador - esqueleto
from src.database.database import transferencias, comprovantes
from loguru import logger


def get_balance(driver_id):
    return 0.0


def saque(driver_id):
    logger.info("saque do entregador: {driver_id}", driver_id=driver_id)
    return "pix enviado"


def get_history(driver_id):
    return []


def get_comprovante_by_transfer(transferencia_id):
    return {}


def list_comprovantes(driver_id):
    return []
