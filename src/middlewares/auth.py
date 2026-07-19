# Auth middleware — guards com FastAPI Depends
from fastapi import Request, Depends
from loguru import logger

from src.utils.tokens import decode_token
from src.database.database import tokens
from src.infra.errors import AuthError


async def auth_required(request: Request) -> dict:
    """Extrai Bearer token, verifica JWT, checa blacklist, retorna payload."""
    logger.debug("middleware: auth_required")

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthError("Cabeçalho de autorização ausente")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("Formato do token inválido. Use: Bearer <token>")

    token = parts[1]

    # Verifica blacklist
    if tokens.exists(token=token):
        raise AuthError("Token revogado. Faça login novamente.")

    try:
        payload = decode_token(token)
    except Exception:
        raise AuthError("Token inválido ou expirado.")

    if "sub" not in payload or "role" not in payload:
        raise AuthError("Payload do token incompleto.")

    return {
        "user_id": payload["sub"],
        "role": payload["role"],
        "email_confirmed": payload.get("email_confirmed", False),
        "token": token,
    }


async def client_required(payload: dict = Depends(auth_required)) -> dict:
    """Verifica se o usuário logado é um cliente."""
    if payload["role"] != "client":
        raise AuthError("Acesso restrito a clientes")
    return payload


async def merchant_required(payload: dict = Depends(auth_required)) -> dict:
    """Verifica se o usuário logado é um merchant."""
    if payload["role"] != "merchant":
        raise AuthError("Acesso restrito a merchants")
    return payload


async def driver_required(payload: dict = Depends(auth_required)) -> dict:
    """Verifica se o usuário logado é um entregador."""
    if payload["role"] != "driver":
        raise AuthError("Acesso restrito a entregadores")
    return payload


async def admin_required(payload: dict = Depends(auth_required)) -> dict:
    """Verifica se o usuário logado é um admin."""
    if payload["role"] != "admin":
        raise AuthError("Acesso restrito a administradores")
    return payload
