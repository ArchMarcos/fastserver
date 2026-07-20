# Merchant authentication — lógica de negócio
from loguru import logger

from src.database.database import merchants, tokens, email_confirmations
from src.database.database import serialize, deserialize
from src.utils.security import encrypt, verify
from src.utils.tokens import create_token, create_email_token, decode_email_token
from src.infra.errors import AuthError, NotFoundError, ValidationError
from src.apps.notifications import email as email_notif, in_app as in_app_notif
from src.infra.config import settings


def register(name, email, phone, password, address, lat=None, lng=None):
    logger.info("cadastro merchant: {email}")

    if merchants.exists(email=email):
        raise ValidationError("Email já cadastrado")
    if merchants.exists(phone=phone):
        raise ValidationError("Telefone já cadastrado")

    hashed = encrypt(password)

    merchant_data = {
        "user_type": "merchant",
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
        "products": [],
        "ordens": [],
        "is_open": False,
        "taxa_delivery": 0.0,
        "categories": [],
        "logo_url": "",
        "rating": 0.0,
        "opening_hours": "",
        "delivery_time": 30,
    }

    serialized = serialize(merchant_data)
    created = merchants.create(**serialized)

    email_token = create_email_token(str(created["id"]), email, "merchant")
    email_notif.send_confirmation(email, name, email_token)
    email_confirmations.create(
        user_id=str(created["id"]),
        email=email,
        token=email_token,
        role="merchant",
    )

    return {
        "message": "Merchant cadastrado com sucesso. Confirme seu e-mail.",
        "user_id": str(created["id"]),
        "email_token": email_token,
    }


def login(ident, password):
    logger.info("login merchant: {ident}")

    user = None
    try:
        user = merchants.first(email=ident)
    except Exception:
        try:
            user = merchants.first(phone=ident)
        except Exception:
            raise NotFoundError("Merchant não encontrado")

    user = deserialize(user)

    if not verify(password, user["password"]):
        raise AuthError("Senha incorreta")

    if not user.get("email_confirmed"):
        raise AuthError("E-mail não confirmado. Verifique sua caixa de entrada ou solicite o reenvio.")

    token = create_token({
        "sub": str(user["id"]),
        "role": "merchant",
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
    logger.info("confirmando e-mail de merchant")

    try:
        payload = decode_email_token(token)
    except Exception:
        raise ValidationError("Token de confirmação inválido ou expirado")

    user_id = payload["sub"]

    record = email_confirmations.first(user_id=user_id, role="merchant")
    if not record:
        raise NotFoundError("Nenhuma solicitação de confirmação encontrada")

    merchants.update({"email_confirmed": True}, id=user_id)
    email_confirmations.delete(id=record["id"])

    user_d = deserialize(merchants.get(user_id))
    email_notif.send_welcome(user_d.get("email", ""), user_d.get("name", ""))
    in_app_notif.send(user_id, "merchant", "Bem-vindo(a)!", f"Loja confirmada. Comece a vender no {settings.PLATFORM_NAME}!")

    return {"message": "E-mail confirmado com sucesso"}


def resend_confirmation(user_id):
    logger.info("reenviando confirmação: {user_id}")

    user_data = merchants.get(user_id)
    if not user_data:
        raise NotFoundError("Merchant não encontrado")

    user_data = deserialize(user_data)
    if user_data.get("email_confirmed"):
        raise ValidationError("E-mail já confirmado")

    email_token = create_email_token(user_id, user_data["email"], "merchant")
    email_confirmations.create(
        user_id=user_id,
        email=user_data["email"],
        token=email_token,
        role="merchant",
    )

    # Reenvia email
    email_notif.send_confirmation(user_data["email"], user_data["name"], email_token)

    return {
        "message": "Novo token de confirmação enviado para seu e-mail",
        "email_token": email_token,
    }


def resend_confirmation_by_email(email):
    """Reenvia confirmação por email (sem autenticação)."""
    logger.info("reenviando confirmação merchant por email: {email}")

    try:
        user_data = merchants.first(email=email)
    except Exception:
        raise NotFoundError("E-mail não encontrado")

    user_data = deserialize(user_data)
    return resend_confirmation(str(user_data["id"]))


def update_field(user_id, field, value):
    logger.info("atualizar merchant {user_id}: {field}", user_id=user_id, field=field)

    user_data = merchants.get(user_id)
    if not user_data:
        raise NotFoundError("Merchant não encontrado")

    allowed_fields = {"name", "phone", "address", "logo_url", "opening_hours", "taxa_delivery"}
    if field not in allowed_fields:
        raise ValidationError(f"Campo '{field}' não pode ser alterado ou não existe")

    merchants.update({field: value}, id=user_id)
    return {"message": f"Campo '{field}' atualizado com sucesso"}


def toggle_open(merchant_id):
    logger.info("alternar abertura: {merchant_id}")

    merchant_data = merchants.get(merchant_id)
    if not merchant_data:
        raise NotFoundError("Merchant não encontrado")

    merchant_data = deserialize(merchant_data)
    new_status = not merchant_data.get("is_open", False)
    merchants.update({"is_open": new_status}, id=merchant_id)

    status_text = "aberto" if new_status else "fechado"
    return {"message": f"Merchant agora está {status_text}", "is_open": new_status}


def logout(token):
    logger.info("logout merchant")

    tokens.create(token=token, revoked=True)
    return {"message": "Logout concluído com sucesso"}


def delete(ident, password):
    logger.info("deletar merchant: {ident}")

    user = None
    try:
        user = merchants.first(email=ident)
    except Exception:
        try:
            user = merchants.first(phone=ident)
        except Exception:
            raise NotFoundError("Merchant não encontrado")

    user = deserialize(user)

    if not verify(password, user["password"]):
        raise AuthError("Senha incorreta")

    merchants.delete(id=user["id"])
    return {"message": "Merchant deletado com sucesso"}


def get_profile(user_id):
    logger.info("perfil do merchant: {user_id}")

    user_data = merchants.get(user_id)
    if not user_data:
        raise NotFoundError("Merchant não encontrado")

    user_data = deserialize(user_data)
    user_data.pop("password", None)
    user_data.pop("px_key", None)

    return user_data
