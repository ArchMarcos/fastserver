# Notificações push - esqueleto (envio direto, sem db)
from loguru import logger


def send_push(user_id, title, body, data=None):
    logger.info("push: {user_id} title: {title}", user_id=user_id, title=title)
    return "push enviado"
