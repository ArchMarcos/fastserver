# Rotas de autenticação — FastAPI Router
from fastapi import APIRouter, Depends, status
from loguru import logger

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
    )


@router.post("/login/client", response_model=TokenResponse)
async def login_client(body: LoginRequest):
    logger.info("POST /auth/login/client")
    return client_app.login(ident=body.ident, password=body.password)


@router.post("/confirm-email/client", response_model=SuccessResponse)
async def confirm_email_client(body: ConfirmEmailRequest):
    logger.info("POST /auth/confirm-email/client")
    return client_app.confirm_email(token=body.token)


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

