# Rotas de pedidos e pagamentos — FastAPI Router
from fastapi import APIRouter, Depends, status
from loguru import logger

from src.schemas.order import CreateOrdemRequest, RateRequest, MerchantActionResponse
from src.schemas.payment import RechargeRequest
from src.schemas.common import SuccessResponse
from src.middlewares.auth import client_required, merchant_required, auth_required
from src.apps.clients import ordem as client_ordem
from src.apps.clients import pay as client_pay
from src.apps.merchant import ordem as merchant_ordem
from src.apps.merchant import pay as merchant_pay

router = APIRouter(prefix="/ordens", tags=["ordens"])


# ========== CLIENTE — PEDIDOS ==========

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_ordem(body: CreateOrdemRequest, payload: dict = Depends(client_required)):
    logger.info("POST /ordens/create")
    return client_ordem.create_ordem(
        client_id=payload["user_id"],
        entregar_em=body.entregar_em,
        obs=body.obs,
        payment_method=body.payment_method,
    )


@router.get("")
async def list_ordens(payload: dict = Depends(client_required)):
    logger.info("GET /ordens")
    return client_ordem.list_ordens(client_id=payload["user_id"])


@router.get("/active")
async def list_ordens_active(payload: dict = Depends(client_required)):
    logger.info("GET /ordens/active")
    return client_ordem.list_ordens_active(client_id=payload["user_id"])


@router.get("/history")
async def list_ordens_history(payload: dict = Depends(client_required)):
    logger.info("GET /ordens/history")
    return client_ordem.list_ordens_history(client_id=payload["user_id"])


# ========== CLIENTE — PAGAMENTOS (LITERAIS PRIMEIRO) ==========

@router.post("/recharge")
async def recharge(body: RechargeRequest, payload: dict = Depends(client_required)):
    logger.info("POST /ordens/recharge")
    return client_pay.recharge(client_id=payload["user_id"], value=body.value)


@router.get("/balance")
async def get_balance(payload: dict = Depends(client_required)):
    logger.info("GET /ordens/balance")
    return client_pay.get_balance(client_id=payload["user_id"])


@router.get("/history/payments")
async def get_pay_history(payload: dict = Depends(client_required)):
    logger.info("GET /ordens/history/payments")
    return client_pay.get_history(client_id=payload["user_id"])


@router.get("/comprovantes")
async def list_comprovantes(payload: dict = Depends(client_required)):
    logger.info("GET /ordens/comprovantes")
    return client_pay.list_comprovantes(client_id=payload["user_id"])


# ========== ROTAS PARAMETRIZADAS (DEPOIS DAS LITERAIS) ==========

@router.get("/{ordem_id}")
async def get_ordem(ordem_id: str, payload: dict = Depends(auth_required)):
    logger.info("GET /ordens/{oid}", oid=ordem_id)
    return client_ordem.get_ordem(ordem_id=ordem_id)


@router.post("/{ordem_id}/cancel", response_model=MerchantActionResponse)
async def cancel_ordem(ordem_id: str, payload: dict = Depends(client_required)):
    logger.info("POST /ordens/{oid}/cancel", oid=ordem_id)
    return client_ordem.cancel_ordem(ordem_id=ordem_id, client_id=payload["user_id"])


@router.post("/{ordem_id}/rate", response_model=SuccessResponse)
async def rate_ordem(ordem_id: str, body: RateRequest, payload: dict = Depends(client_required)):
    logger.info("POST /ordens/{oid}/rate", oid=ordem_id)
    return client_ordem.rate_ordem(ordem_id=ordem_id, score=body.score, comment=body.comment)


@router.post("/{ordem_id}/pay")
async def pagar_ordem(ordem_id: str, payload: dict = Depends(client_required)):
    logger.info("POST /ordens/{oid}/pay", oid=ordem_id)
    return client_pay.pagar_ordem(ordem_id=ordem_id, client_id=payload["user_id"])
    logger.info("POST /ordens/recharge")
    return client_pay.recharge(client_id=payload["user_id"], value=body.value)


@router.get("/balance")
async def get_balance(payload: dict = Depends(client_required)):
    logger.info("GET /ordens/balance")
    return client_pay.get_balance(client_id=payload["user_id"])


@router.get("/history/payments")
async def get_pay_history(payload: dict = Depends(client_required)):
    logger.info("GET /ordens/history/payments")
    return client_pay.get_history(client_id=payload["user_id"])


@router.get("/comprovantes")
async def list_comprovantes(payload: dict = Depends(client_required)):
    logger.info("GET /ordens/comprovantes")
    return client_pay.list_comprovantes(client_id=payload["user_id"])


# ========== MERCHANT — SUB-ORDENS ==========

@router.get("/merchant/pending")
async def merchant_list_pending(payload: dict = Depends(merchant_required)):
    logger.info("GET /ordens/merchant/pending")
    return merchant_ordem.list_pending(merchant_id=payload["user_id"])


@router.get("/merchant/all")
async def merchant_list_all(payload: dict = Depends(merchant_required)):
    logger.info("GET /ordens/merchant/all")
    return merchant_ordem.list_all(merchant_id=payload["user_id"])


@router.get("/merchant/active")
async def merchant_list_active(payload: dict = Depends(merchant_required)):
    logger.info("GET /ordens/merchant/active")
    return merchant_ordem.list_active(merchant_id=payload["user_id"])


@router.get("/merchant/history")
async def merchant_list_history(payload: dict = Depends(merchant_required)):
    logger.info("GET /ordens/merchant/history")
    return merchant_ordem.list_history(merchant_id=payload["user_id"])


@router.post("/sub-ordens/{sub_id}/accept", response_model=MerchantActionResponse)
async def accept_sub(sub_id: str, payload: dict = Depends(merchant_required)):
    logger.info("POST /ordens/sub-ordens/{sid}/accept", sid=sub_id)
    return merchant_ordem.accept(sub_ordem_id=sub_id)


@router.post("/sub-ordens/{sub_id}/refuse", response_model=MerchantActionResponse)
async def refuse_sub(sub_id: str, payload: dict = Depends(merchant_required)):
    logger.info("POST /ordens/sub-ordens/{sid}/refuse", sid=sub_id)
    return merchant_ordem.refuse(sub_ordem_id=sub_id)


@router.post("/sub-ordens/{sub_id}/start-preparing", response_model=MerchantActionResponse)
async def start_preparing(sub_id: str, payload: dict = Depends(merchant_required)):
    logger.info("POST /ordens/sub-ordens/{sid}/start-preparing", sid=sub_id)
    return merchant_ordem.start_preparing(sub_ordem_id=sub_id)


@router.post("/sub-ordens/{sub_id}/mark-ready", response_model=MerchantActionResponse)
async def mark_ready(sub_id: str, payload: dict = Depends(merchant_required)):
    logger.info("POST /ordens/sub-ordens/{sid}/mark-ready", sid=sub_id)
    return merchant_ordem.mark_ready(sub_ordem_id=sub_id)


@router.post("/sub-ordens/{sub_id}/waiting-driver", response_model=MerchantActionResponse)
async def waiting_driver(sub_id: str, payload: dict = Depends(merchant_required)):
    logger.info("POST /ordens/sub-ordens/{sid}/waiting-driver", sid=sub_id)
    return merchant_ordem.waiting_driver(sub_ordem_id=sub_id)


@router.post("/sub-ordens/{sub_id}/collected", response_model=MerchantActionResponse)
async def collected_by_driver(sub_id: str, payload: dict = Depends(merchant_required)):
    logger.info("POST /ordens/sub-ordens/{sid}/collected", sid=sub_id)
    return merchant_ordem.mark_collected(sub_ordem_id=sub_id)


# ========== MERCHANT — FINANÇAS ==========

@router.get("/merchant/earnings")
async def merchant_calc_earnings(payload: dict = Depends(merchant_required)):
    logger.info("GET /ordens/merchant/earnings")
    return {"earnings": merchant_ordem.calc_earnings(merchant_id=payload["user_id"])}


@router.get("/merchant/balance")
async def merchant_balance(payload: dict = Depends(merchant_required)):
    logger.info("GET /ordens/merchant/balance")
    return merchant_pay.get_balance(merchant_id=payload["user_id"])


@router.get("/merchant/liquid")
async def merchant_liquid(payload: dict = Depends(merchant_required)):
    logger.info("GET /ordens/merchant/liquid")
    return {"liquid": merchant_pay.calc_liquid(merchant_id=payload["user_id"])}


@router.post("/merchant/saque")
async def merchant_saque(payload: dict = Depends(merchant_required)):
    logger.info("POST /ordens/merchant/saque")
    return merchant_pay.saque(merchant_id=payload["user_id"])


@router.get("/merchant/comprovantes")
async def merchant_comprovantes(payload: dict = Depends(merchant_required)):
    logger.info("GET /ordens/merchant/comprovantes")
    return merchant_pay.list_comprovantes(merchant_id=payload["user_id"])
