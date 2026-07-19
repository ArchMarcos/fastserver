# Vitrine do cliente - esqueleto
from src.database.database import products, merchants
from loguru import logger


def list_by_category(categoria):
    logger.info("vitrine por categoria: {categoria}")
    return []


def search(query):
    logger.info("vitrine busca: {query}")
    return []


def list_by_merchant(merchant_id):
    return []


def list_open_merchants():
    return []


def get_product(product_id):
    return {}


def list_categories():
    return []
