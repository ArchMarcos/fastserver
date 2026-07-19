# Driver authentication - esqueleto
from src.database.database import drivers, tokens, email_confirmations
from src.globals.glob import Driver
from src.utils.tokens import create_email_token, verify_email_token, decode_email_token
from src.utils.security import encrypt
from loguru import logger


def register(name, email, phone, password, address, veiculo):
    logger.info("cadastro entregador: {email}")
    return "entregador cadastrado, confirme seu e-mail"


def login(ident, password):
    logger.info("login entregador: {ident}")
    return "entregador logado"


def confirm_email(token):
    logger.info("confirmando e-mail")
    return "e-mail confirmado"


def resend_confirmation(user_id):
    logger.info("reenviando confirmação: {user_id}")
    return "novo e-mail de confirmação enviado"


def go_online(driver_id):
    logger.info("entregador online: {driver_id}")
    return "entregador online"


def go_offline(driver_id):
    logger.info("entregador offline: {driver_id}")
    return "entregador offline"


def update_field(user_id, field, value):
    logger.info("atualizar entregador {user_id}: {field}", user_id=user_id, field=field)
    return "campo atualizado"


def logout(token):
    logger.info("logout entregador")
    return "logout concluído"


def delete(ident, password):
    logger.info("deletar entregador: {ident}")
    return "entregador deletado"


def get_profile(user_id):
    return {}
