# Cart do cliente - esqueleto
from src.database.database import carts
from loguru import logger


def add_to_cart(client_id, product_id, merchant_id, quantidade, acompanhamentos, obs=""):
    logger.info("adicionar ao carrinho: {client_id} produto: {product_id}", client_id=client_id, product_id=product_id)
    return "item adicionado ao carrinho"


def remove_from_cart(client_id, product_id):
    logger.info("remover do carrinho: {client_id} produto: {product_id}", client_id=client_id, product_id=product_id)
    return "item removido do carrinho"


def update_quantity(client_id, product_id, quantidade):
    logger.info("atualizar quantidade: {client_id} produto: {product_id} qtd: {quantidade}", client_id=client_id, product_id=product_id, quantidade=quantidade)
    return "quantidade atualizada"


def update_obs(client_id, product_id, obs):
    logger.info("atualizar observação: {client_id} produto: {product_id}", client_id=client_id, product_id=product_id)
    return "observação atualizada"


def get_cart(client_id):
    return []


def clear_cart(client_id):
    logger.info("limpar carrinho: {client_id}")
    return "carrinho limpo"


def calc_cart_totals(client_id):
    return {"total_products": 0, "total_delivery_fee": 0, "total_platform_tax": 0, "total": 0}
