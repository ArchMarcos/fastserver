# Client authentication — lógica de negócio
from loguru import logger

from src.database.database import clients, tokens, email_confirmations
from src.database.database import serialize, deserialize
from src.utils.security import encrypt, verify
from src.utils.tokens import create_token, create_email_token, decode_email_token
from src.infra.errors import AuthError, NotFoundError, ValidationError
from src.apps.notifications import email as email_notif, in_app as in_app_notif
from src.infra.config import settings


def register(name, email, phone, password, address):
    logger.info("cadastro cliente: {email}")

    if clients.exists(email=email):
        raise ValidationError("Email já cadastrado")
    if clients.exists(phone=phone):
        raise ValidationError("Telefone já cadastrado")

    hashed = encrypt(password)

    user_data = {
        "user_type": "client",
        "avatar_url": "",
        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed,
        "px_key": "",
        "address": address,
        "balance": 0.0,
        "status": True,
        "email_confirmed": False,
        "notify": [],
        "cart": [],
        "ordem": [],
        "favorites": [],
        "addresses": [],
        "active_ordem": "",
    }

    serialized = serialize(user_data)
    created = clients.create(**serialized)

    # Gera token de confirmação de email
    email_token = create_email_token(str(created["id"]), email)
    email_confirmations.create(
        user_id=str(created["id"]),
        email=email,
        token=email_token,
    )

    # Envia email de confirmação (não bloqueante)
    email_notif.send_confirmation(email, name, email_token)

    return {
        "message": "Cliente cadastrado com sucesso. Confirme seu e-mail.",
        "user_id": str(created["id"]),
        "email_token": email_token,
    }


def login(ident, password):
    logger.info("login cliente: {ident}")

    user = None
    try:
        user = clients.first(email=ident)
    except Exception:
        try:
            user = clients.first(phone=ident)
        except Exception:
            raise NotFoundError("Cliente não encontrado")

    user = deserialize(user)

    if not verify(password, user["password"]):
        raise AuthError("Senha incorreta")

    token = create_token({
        "sub": str(user["id"]),
        "role": "client",
        "email_confirmed": user.get("email_confirmed", False),
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user["id"]),
        "name": user["name"],
        "email": user["email"],
    }


def confirm_email(token):
    logger.info("confirmando e-mail de cliente")

    try:
        payload = decode_email_token(token)
    except Exception:
        raise ValidationError("Token de confirmação inválido ou expirado")

    user_id = payload["sub"]

    records = email_confirmations.find(user_id=user_id)
    if not records:
        raise NotFoundError("Nenhuma solicitação de confirmação encontrada")

    clients.update({"email_confirmed": True}, id=user_id)
    email_confirmations.delete(user_id=user_id)

    # Notificações pós-confirmação
    user = deserialize(clients.get(user_id))
    email_notif.send_welcome(user.get("email", ""), user.get("name", ""))
    in_app_notif.send(user_id, "client", "Bem-vindo(a)!", f"Conta confirmada. Aproveite o {settings.PLATFORM_NAME}!")

    return {"message": "E-mail confirmado com sucesso"}


def resend_confirmation(user_id):
    logger.info("reenviando confirmação: {user_id}")

    user_data = clients.get(user_id)
    if not user_data:
        raise NotFoundError("Cliente não encontrado")

    user_data = deserialize(user_data)
    if user_data.get("email_confirmed"):
        raise ValidationError("E-mail já confirmado")

    email_token = create_email_token(user_id, user_data["email"])
    email_confirmations.create(
        user_id=user_id,
        email=user_data["email"],
        token=email_token,
    )

    return {
        "message": "Novo token de confirmação gerado",
        "email_token": email_token,
    }


def update_field(user_id, field, value):
    logger.info("atualizar cliente {user_id}: {field}", user_id=user_id, field=field)

    user_data = clients.get(user_id)
    if not user_data:
        raise NotFoundError("Cliente não encontrado")

    allowed_fields = {"name", "phone", "address", "avatar_url", "px_key"}
    if field not in allowed_fields:
        raise ValidationError(f"Campo '{field}' não pode ser alterado ou não existe")

    clients.update({field: value}, id=user_id)
    return {"message": f"Campo '{field}' atualizado com sucesso"}


def logout(token):
    logger.info("logout cliente")

    tokens.create(token=token, revoked=True)
    return {"message": "Logout concluído com sucesso"}


def delete(ident, password):
    logger.info("deletar cliente: {ident}")

    user = None
    try:
        user = clients.first(email=ident)
    except Exception:
        try:
            user = clients.first(phone=ident)
        except Exception:
            raise NotFoundError("Cliente não encontrado")

    user = deserialize(user)

    if not verify(password, user["password"]):
        raise AuthError("Senha incorreta")

    clients.delete(id=user["id"])
    return {"message": "Cliente deletado com sucesso"}


def get_profile(user_id):
    logger.info("perfil do cliente: {user_id}")

    user_data = clients.get(user_id)
    if not user_data:
        raise NotFoundError("Cliente não encontrado")

    user_data = deserialize(user_data)
    user_data.pop("password", None)
    user_data.pop("px_key", None)

    return user_data
