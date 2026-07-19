# Favoritos do cliente - esqueleto
from src.database.database import clients
from loguru import logger


def list_favorites(client_id):
    return []


def add_favorite(client_id, merchant_id):
    logger.info("adicionar favorito: {client_id} merchant: {merchant_id}", client_id=client_id, merchant_id=merchant_id)
    return "favorito adicionado"


def remove_favorite(client_id, merchant_id):
    logger.info("remover favorito: {client_id} merchant: {merchant_id}", client_id=client_id, merchant_id=merchant_id)
    return "favorito removido"


def is_favorite(client_id, merchant_id):
    return False
