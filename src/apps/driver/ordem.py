# Ordem do entregador - esqueleto
from src.database.database import ordens, sub_ordens, drivers, driver_history
from loguru import logger


def list_available(driver_id):
    return []


def accept_order(driver_id, ordem_id):
    logger.info("entregador aceitou: {driver_id} ordem: {ordem_id}", driver_id=driver_id, ordem_id=ordem_id)
    return "ordem aceita pelo entregador"


def mark_collected(ordem_id):
    logger.info("coletado: {ordem_id}", ordem_id=ordem_id)
    return "pedido coletado"


def mark_in_delivery(ordem_id):
    logger.info("saiu para entrega: {ordem_id}", ordem_id=ordem_id)
    return "saiu para entrega"


def mark_delivered(ordem_id):
    logger.info("entregue: {ordem_id}", ordem_id=ordem_id)
    return "pedido entregue"


def reject_order(driver_id, ordem_id):
    logger.info("entregador recusou: {driver_id} ordem: {ordem_id}", driver_id=driver_id, ordem_id=ordem_id)
    return "ordem recusada"


def get_current(driver_id):
    return {}


def get_history(driver_id):
    return []


def calc_earnings(driver_id):
    return 0.0
