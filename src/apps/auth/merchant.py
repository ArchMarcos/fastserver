# Merchant authentication - esqueleto
from src.database.database import merchants, tokens, email_confirmations
from src.globals.glob import Merchant
from src.utils.tokens import create_email_token, verify_email_token, decode_email_token
from src.utils.security import encrypt
from loguru import logger


def register(name, email, phone, password, address):
    logger.info("cadastro merchant: {email}")
    return "merchant cadastrado, confirme seu e-mail"


def login(ident, password):
    logger.info("login merchant: {ident}")
    return "merchant logado"


def confirm_email(token):
    logger.info("confirmando e-mail")
    return "e-mail confirmado"


def resend_confirmation(user_id):
    logger.info("reenviando confirmação: {user_id}")
    return "novo e-mail de confirmação enviado"


def update_field(user_id, field, value):
    logger.info("atualizar merchant {user_id}: {field}", user_id=user_id, field=field)
    return "campo atualizado"


def toggle_open(merchant_id):
    logger.info("alternar abertura: {merchant_id}")
    return "merchant aberto/fechado"


def logout(token):
    logger.info("logout merchant")
    return "logout concluído"


def delete(ident, password):
    logger.info("deletar merchant: {ident}")
    return "merchant deletado"


def get_profile(user_id):
    return {}
