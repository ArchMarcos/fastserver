# Merchant products - esqueleto
from src.database.database import products
from src.globals.glob import Produto
from loguru import logger


def new_product(merchant_id, name, description, images, acompanhamentos, price, categoria):
    logger.info("novo produto do merchant: {merchant_id} nome: {name}", merchant_id=merchant_id, name=name)
    return "produto adicionado"


def update_product(product_id, field, value):
    logger.info("produto atualizado: {product_id} campo: {field}", product_id=product_id, field=field)
    return "produto atualizado"


def remove_product(product_id):
    logger.info("produto removido: {product_id}", product_id=product_id)
    return "produto removido"


def list_my_products(merchant_id):
    return []


def toggle_active(product_id):
    logger.info("ativar/desativar produto: {product_id}", product_id=product_id)
    return "produto ativado/desativado"


def apply_discount(product_id, discount):
    logger.info("desconto aplicado: {product_id} valor: {discount}", product_id=product_id, discount=discount)
    return "desconto aplicado"
