# Envio de e-mails - esqueleto
from loguru import logger
from src.infra.config import settings

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
SMTP_FROM = settings.SMTP_FROM


def send_confirmation(email, token):
    logger.info("e-mail de confirmação para: {email}")
    return "e-mail de confirmação enviado"


def send_welcome(email, name):
    logger.info("boas-vindas para: {email}")
    return "e-mail de boas-vindas enviado"


def send_reset_password(email, token):
    logger.info("redefinição de senha para: {email}")
    return "e-mail de redefinição enviado"


def send_receipt(email, comprovante):
    logger.info("comprovante para: {email}")
    return "comprovante enviado"


def send_email(to, subject, body):
    logger.info("e-mail para {to}: {subject}")
    return "e-mail enviado"
