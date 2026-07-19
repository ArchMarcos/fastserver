# Notificações in-app - esqueleto (envio direto, sem db)
from loguru import logger


def send(user_id, title, body, tipo="info"):
    logger.info("notificação in-app: {user_id} type: {tipo}", user_id=user_id, tipo=tipo)
    return {"user_id": user_id, "title": title, "body": body, "tipo": tipo}


def list_by_user(user_id):
    return []


def clear(user_id):
    logger.info("notificações limpas: {user_id}", user_id=user_id)
    return "notificações limpas"
