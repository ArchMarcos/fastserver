# Driver authentication — lógica de negócio
from loguru import logger

from src.database.database import drivers, tokens, email_confirmations
from src.database.database import serialize, deserialize
from src.utils.security import encrypt, verify
from src.utils.tokens import create_token, create_email_token, decode_email_token
from src.infra.errors import AuthError, NotFoundError, ValidationError
from src.apps.notifications import email as email_notif, in_app as in_app_notif
from src.infra.config import settings


def register(name, email, phone, password, address, veiculo, lat=None, lng=None):
    logger.info("cadastro entregador: {email}")

    if drivers.exists(email=email):
        raise ValidationError("Email já cadastrado")
    if drivers.exists(phone=phone):
        raise ValidationError("Telefone já cadastrado")

    hashed = encrypt(password)

    driver_data = {
        "user_type": "driver",
        "avatar_url": "",
        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed,
        "px_key": "",
        "address": address,
        "lat": lat or "",
        "lng": lng or "",
        "balance": 0.0,
        "status": True,
        "email_confirmed": False,
        "notify": [],
        "veiculo": veiculo,
        "current_ordem": "",
        "ordens_disponiveis": [],
        "is_online": False,
        "location": "",
    }

    serialized = serialize(driver_data)
    created = drivers.create(**serialized)

    email_token = create_email_token(str(created["id"]), email)
    email_notif.send_confirmation(email, name, email_token)
    email_confirmations.create(
        user_id=str(created["id"]),
        email=email,
        token=email_token,
    )

    return {
        "message": "Entregador cadastrado com sucesso. Confirme seu e-mail.",
        "user_id": str(created["id"]),
        "email_token": email_token,
    }


def login(ident, password):
    logger.info("login entregador: {ident}")

    user = None
    try:
        user = drivers.first(email=ident)
    except Exception:
        try:
            user = drivers.first(phone=ident)
        except Exception:
            raise NotFoundError("Entregador não encontrado")

    user = deserialize(user)

    if not verify(password, user["password"]):
        raise AuthError("Senha incorreta")

    if not user.get("email_confirmed"):
        raise AuthError("E-mail não confirmado. Verifique sua caixa de entrada ou solicite o reenvio.")

    token = create_token({
        "sub": str(user["id"]),
        "role": "driver",
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
    logger.info("confirmando e-mail de entregador")

    try:
        payload = decode_email_token(token)
    except Exception:
        raise ValidationError("Token de confirmação inválido ou expirado")

    user_id = payload["sub"]

    records = email_confirmations.find(user_id=user_id)
    if not records:
        raise NotFoundError("Nenhuma solicitação de confirmação encontrada")

    drivers.update({"email_confirmed": True}, id=user_id)
    email_confirmations.delete(user_id=user_id)

    user_d = deserialize(drivers.get(user_id))
    email_notif.send_welcome(user_d.get("email", ""), user_d.get("name", ""))
    in_app_notif.send(user_id, "driver", "Bem-vindo(a)!", f"Conta confirmada. Comece a entregar no {settings.PLATFORM_NAME}!")

    return {"message": "E-mail confirmado com sucesso"}


def resend_confirmation(user_id):
    logger.info("reenviando confirmação: {user_id}")

    user_data = drivers.get(user_id)
    if not user_data:
        raise NotFoundError("Entregador não encontrado")

    user_data = deserialize(user_data)
    if user_data.get("email_confirmed"):
        raise ValidationError("E-mail já confirmado")

    email_token = create_email_token(user_id, user_data["email"])
    email_confirmations.create(
        user_id=user_id,
        email=user_data["email"],
        token=email_token,
    )

    # Reenvia email
    email_notif.send_confirmation(user_data["email"], user_data["name"], email_token)

    return {
        "message": "Novo token de confirmação enviado para seu e-mail",
        "email_token": email_token,
    }


def resend_confirmation_by_email(email):
    """Reenvia confirmação por email (sem autenticação)."""
    logger.info("reenviando confirmação driver por email: {email}")

    try:
        user_data = drivers.first(email=email)
    except Exception:
        raise NotFoundError("E-mail não encontrado")

    user_data = deserialize(user_data)
    return resend_confirmation(str(user_data["id"]))


def go_online(driver_id):
    logger.info("entregador online: {driver_id}")

    driver_data = drivers.get(driver_id)
    if not driver_data:
        raise NotFoundError("Entregador não encontrado")

    drivers.update({"is_online": True}, id=driver_id)
    return {"message": "Entregador agora está online"}


def go_offline(driver_id):
    logger.info("entregador offline: {driver_id}")

    driver_data = drivers.get(driver_id)
    if not driver_data:
        raise NotFoundError("Entregador não encontrado")

    drivers.update({"is_online": False}, id=driver_id)
    return {"message": "Entregador agora está offline"}


def update_field(user_id, field, value):
    logger.info("atualizar entregador {user_id}: {field}", user_id=user_id, field=field)

    user_data = drivers.get(user_id)
    if not user_data:
        raise NotFoundError("Entregador não encontrado")

    allowed_fields = {"name", "phone", "address", "avatar_url", "veiculo"}
    if field not in allowed_fields:
        raise ValidationError(f"Campo '{field}' não pode ser alterado ou não existe")

    drivers.update({field: value}, id=user_id)
    return {"message": f"Campo '{field}' atualizado com sucesso"}


def logout(token):
    logger.info("logout entregador")

    tokens.create(token=token, revoked=True)
    return {"message": "Logout concluído com sucesso"}


def delete(ident, password):
    logger.info("deletar entregador: {ident}")

    user = None
    try:
        user = drivers.first(email=ident)
    except Exception:
        try:
            user = drivers.first(phone=ident)
        except Exception:
            raise NotFoundError("Entregador não encontrado")

    user = deserialize(user)

    if not verify(password, user["password"]):
        raise AuthError("Senha incorreta")

    drivers.delete(id=user["id"])
    return {"message": "Entregador deletado com sucesso"}


def get_profile(user_id):
    logger.info("perfil do entregador: {user_id}")

    user_data = drivers.get(user_id)
    if not user_data:
        raise NotFoundError("Entregador não encontrado")

    user_data = deserialize(user_data)
    user_data.pop("password", None)
    user_data.pop("px_key", None)

    return user_data
