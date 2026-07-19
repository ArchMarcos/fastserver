# Token JWT utilities - esqueleto
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from loguru import logger
from src.infra.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_EXPIRE_MINUTES
EMAIL_TOKEN_EXPIRE_MINUTES = settings.JWT_EMAIL_EXPIRE_MINUTES


def create_token(data: dict[str, Any], expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_email_token(user_id: str, email: str) -> str:
    logger.info("criando token de e-mail: {email}")
    data = {"sub": user_id, "email": email, "type": "email_confirmation"}
    return create_token(data, expires_minutes=EMAIL_TOKEN_EXPIRE_MINUTES)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def decode_email_token(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "email_confirmation":
        logger.warning("token não é de confirmação de e-mail")
        raise ValueError("Token não é de confirmação de e-mail")
    return payload


def verify_token(token: str) -> bool:
    try:
        decode_token(token)
        return True
    except jwt.ExpiredSignatureError:
        logger.warning("token expirado")
        return False
    except jwt.InvalidTokenError:
        logger.warning("token inválido")
        return False


def verify_email_token(token: str) -> bool:
    try:
        decode_email_token(token)
        return True
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        logger.warning("token de e-mail inválido")
        return False
