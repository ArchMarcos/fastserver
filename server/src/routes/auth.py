# Rotas de autenticação — FastAPI Router
from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from loguru import logger

from src.infra.errors import ValidationError
from src.schemas.auth import (
    RegisterClientRequest,
    RegisterMerchantRequest,
    RegisterDriverRequest,
    LoginRequest,
    ConfirmEmailRequest,
    RegisterResponse,
    TokenResponse,
)
from src.schemas.common import SuccessResponse
from src.middlewares.auth import auth_required, client_required, merchant_required, driver_required
from src.apps.auth import client as client_app
from src.apps.auth import merchant as merchant_app
from src.apps.auth import driver as driver_app

router = APIRouter(prefix="/auth", tags=["auth"])


# ========== CONFIRMAÇÃO UNIFICADA (via link do email) ==========

@router.get("/confirm-email")
async def confirm_email_get(token: str):
    """Confirmação via link de email (GET). Auto-detecta a role e retorna HTML."""
    logger.info("GET /auth/confirm-email")
    from src.database.database import clients, merchants, drivers
    from src.utils.tokens import decode_email_token

    try:
        payload = decode_email_token(token)
    except Exception:
        return HTMLResponse(_confirm_html("Token inválido", "O link de confirmação expirou ou é inválido.", False))

    user_id = payload["sub"]

    for col, app, role in [
        (clients, client_app, "client"),
        (merchants, merchant_app, "merchant"),
        (drivers, driver_app, "driver"),
    ]:
        try:
            col.get(user_id)
            app.confirm_email(token)
            return HTMLResponse(_confirm_html("E-mail confirmado! 🎉", f"Sua conta como <strong>{role}</strong> está ativa. Volte ao app e faça login.", True))
        except Exception:
            continue

    return HTMLResponse(_confirm_html("Usuário não encontrado", "Não foi possível identificar sua conta.", False))


def _confirm_html(title: str, message: str, success: bool) -> str:
    color = "#7CB9E8" if success else "#ef4444"
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>body{{font-family:'Inter',system-ui,sans-serif;background:#F5FAFD;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:20px}}</style>
</head><body>
<div style="background:white;border-radius:16px;padding:48px 32px;text-align:center;max-width:420px;box-shadow:0 2px 12px rgba(0,0,0,0.06)">
<div style="font-size:48px;margin-bottom:16px">{"✅" if success else "❌"}</div>
<h1 style="margin:0 0 8px;font-size:22px;color:{color}">{title}</h1>
<p style="color:#555;line-height:1.6;margin:16px 0 24px">{message}</p>
<a href="/auth/login.html" style="display:inline-block;padding:14px 36px;background:{color};color:white;text-decoration:none;border-radius:10px;font-weight:600;font-size:14px">Ir para o login</a>
</div></body></html>"""


# ========== CLIENTE ==========

@router.post("/register/client", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_client(body: RegisterClientRequest):
    logger.info("POST /auth/register/client")
    return client_app.register(
        name=body.name,
        email=body.email,
        phone=body.phone,
        password=body.password,
        address=body.address,
        lat=body.lat,
        lng=body.lng,
    )


@router.post("/login/client", response_model=TokenResponse)
async def login_client(body: LoginRequest):
    logger.info("POST /auth/login/client")
    return client_app.login(ident=body.ident, password=body.password)


@router.post("/confirm-email/client", response_model=SuccessResponse)
async def confirm_email_client(body: ConfirmEmailRequest):
    logger.info("POST /auth/confirm-email/client")
    return client_app.confirm_email(token=body.token)


@router.post("/resend-confirmation/public", response_model=SuccessResponse)
async def resend_confirmation_public(body: dict):
    """Reenvia email de confirmação sem autenticação (para usuários que não conseguem logar)."""
    logger.info("POST /auth/resend-confirmation/public")
    email = body.get("email", "")
    role = body.get("role", "")
    if not email or role not in ("client", "merchant", "driver"):
        raise ValidationError("Email e role são obrigatórios")
    apps = {"client": client_app, "merchant": merchant_app, "driver": driver_app}
    return apps[role].resend_confirmation_by_email(email)


@router.post("/resend-confirmation/client", response_model=SuccessResponse)
async def resend_confirmation_client(payload: dict = Depends(client_required)):
    logger.info("POST /auth/resend-confirmation/client")
    return client_app.resend_confirmation(user_id=payload["user_id"])


@router.post("/logout/client", response_model=SuccessResponse)
async def logout_client(payload: dict = Depends(client_required)):
    logger.info("POST /auth/logout/client")
    return client_app.logout(token=payload["token"])


@router.get("/me/client")
async def get_profile_client(payload: dict = Depends(client_required)):
    logger.info("GET /auth/me/client")
    return client_app.get_profile(user_id=payload["user_id"])


# ========== MERCHANT ==========

@router.post("/register/merchant", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_merchant(body: RegisterMerchantRequest):
    logger.info("POST /auth/register/merchant")
    return merchant_app.register(
        name=body.name,
        email=body.email,
        phone=body.phone,
        password=body.password,
        address=body.address,
        lat=body.lat,
        lng=body.lng,
    )


@router.post("/login/merchant", response_model=TokenResponse)
async def login_merchant(body: LoginRequest):
    logger.info("POST /auth/login/merchant")
    return merchant_app.login(ident=body.ident, password=body.password)


@router.post("/confirm-email/merchant", response_model=SuccessResponse)
async def confirm_email_merchant(body: ConfirmEmailRequest):
    logger.info("POST /auth/confirm-email/merchant")
    return merchant_app.confirm_email(token=body.token)


@router.post("/resend-confirmation/merchant", response_model=SuccessResponse)
async def resend_confirmation_merchant(payload: dict = Depends(merchant_required)):
    logger.info("POST /auth/resend-confirmation/merchant")
    return merchant_app.resend_confirmation(user_id=payload["user_id"])


@router.post("/logout/merchant", response_model=SuccessResponse)
async def logout_merchant(payload: dict = Depends(merchant_required)):
    logger.info("POST /auth/logout/merchant")
    return merchant_app.logout(token=payload["token"])


@router.get("/me/merchant")
async def get_profile_merchant(payload: dict = Depends(merchant_required)):
    logger.info("GET /auth/me/merchant")
    return merchant_app.get_profile(user_id=payload["user_id"])


# ========== ENTREGADOR ==========

@router.post("/register/driver", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_driver(body: RegisterDriverRequest):
    logger.info("POST /auth/register/driver")
    return driver_app.register(
        name=body.name,
        email=body.email,
        phone=body.phone,
        password=body.password,
        address=body.address,
        veiculo=body.veiculo,
        lat=body.lat,
        lng=body.lng,
    )


@router.post("/login/driver", response_model=TokenResponse)
async def login_driver(body: LoginRequest):
    logger.info("POST /auth/login/driver")
    return driver_app.login(ident=body.ident, password=body.password)


@router.post("/confirm-email/driver", response_model=SuccessResponse)
async def confirm_email_driver(body: ConfirmEmailRequest):
    logger.info("POST /auth/confirm-email/driver")
    return driver_app.confirm_email(token=body.token)


@router.post("/resend-confirmation/driver", response_model=SuccessResponse)
async def resend_confirmation_driver(payload: dict = Depends(driver_required)):
    logger.info("POST /auth/resend-confirmation/driver")
    return driver_app.resend_confirmation(user_id=payload["user_id"])


@router.post("/logout/driver", response_model=SuccessResponse)
async def logout_driver(payload: dict = Depends(driver_required)):
    logger.info("POST /auth/logout/driver")
    return driver_app.logout(token=payload["token"])


@router.get("/me/driver")
async def get_profile_driver(payload: dict = Depends(driver_required)):
    logger.info("GET /auth/me/driver")
    return driver_app.get_profile(user_id=payload["user_id"])

