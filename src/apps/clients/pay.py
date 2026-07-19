# Pagamento do cliente - esqueleto
from src.database.database import transferencias, recargas, comprovantes
from loguru import logger


def pagar_ordem(ordem_id, client_id):
    logger.info("pagamento da ordem: {ordem_id} cliente: {client_id}", ordem_id=ordem_id, client_id=client_id)
    return "pagamento confirmado, ordem iniciada"


def recharge(client_id, value):
    logger.info("recarga: {client_id} valor: {value}", client_id=client_id, value=value)
    return f"valor {value} adicionado a sua conta"


def get_balance(client_id):
    return 0.0


def get_history(client_id):
    return []


def get_comprovante_by_transfer(transferencia_id):
    return {}


def get_comprovante_by_recharge(recarga_id):
    return {}


def list_comprovantes(client_id):
    return []
