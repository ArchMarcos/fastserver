# Rotas do entregador — FastAPI Router
from fastapi import APIRouter, Depends, Query, status
from loguru import logger

from src.schemas.driver import LocationUpdateRequest
from src.schemas.common import SuccessResponse
from src.middlewares.auth import driver_required
from src.apps.auth import driver as driver_app
from src.apps.driver import ordem as driver_ordem
from src.apps.driver import location as driver_loc
from src.apps.driver import pay as driver_pay

router = APIRouter(prefix="/drivers", tags=["drivers"])


# ── Perfil ──

@router.get("/profile")
async def get_profile(payload: dict = Depends(driver_required)):
    logger.info("GET /drivers/profile")
    return driver_app.get_profile(user_id=payload["user_id"])


@router.patch("/profile", response_model=SuccessResponse)
async def update_profile(field: str = Query(...), value: str = Query(...), payload: dict = Depends(driver_required)):
    logger.info("PATCH /drivers/profile")
    return driver_app.update_field(user_id=payload["user_id"], field=field, value=value)


# ── Online/Offline ──

@router.post("/online", response_model=SuccessResponse)
async def go_online(payload: dict = Depends(driver_required)):
    logger.info("POST /drivers/online")
    return driver_app.go_online(driver_id=payload["user_id"])


@router.post("/offline", response_model=SuccessResponse)
async def go_offline(payload: dict = Depends(driver_required)):
    logger.info("POST /drivers/offline")
    return driver_app.go_offline(driver_id=payload["user_id"])


# ── Localização ──

@router.post("/location")
async def update_location(body: LocationUpdateRequest, payload: dict = Depends(driver_required)):
    logger.info("POST /drivers/location")
    return driver_loc.update_location(driver_id=payload["user_id"], lat=body.lat, lng=body.lng)


@router.get("/location")
async def get_location(payload: dict = Depends(driver_required)):
    logger.info("GET /drivers/location")
    return driver_loc.get_location(driver_id=payload["user_id"])


@router.get("/location/nearby")
async def get_nearby(
    lat: float = Query(...), lng: float = Query(...), radius_km: float = Query(default=5.0),
    payload: dict = Depends(driver_required),
):
    logger.info("GET /drivers/location/nearby")
    return driver_loc.get_nearby_drivers(lat=lat, lng=lng, radius_km=radius_km)


# ── Pedidos ──

@router.get("/orders/available")
async def list_available(payload: dict = Depends(driver_required)):
    logger.info("GET /drivers/orders/available")
    return driver_ordem.list_available(driver_id=payload["user_id"])


@router.post("/orders/{ordem_id}/accept")
async def accept_order(ordem_id: str, payload: dict = Depends(driver_required)):
    logger.info("POST /drivers/orders/{oid}/accept", oid=ordem_id)
    return driver_ordem.accept_order(driver_id=payload["user_id"], ordem_id=ordem_id)


@router.post("/orders/{ordem_id}/reject")
async def reject_order(ordem_id: str, payload: dict = Depends(driver_required)):
    logger.info("POST /drivers/orders/{oid}/reject", oid=ordem_id)
    return driver_ordem.reject_order(driver_id=payload["user_id"], ordem_id=ordem_id)


@router.post("/orders/{ordem_id}/in-delivery")
async def mark_in_delivery(ordem_id: str, payload: dict = Depends(driver_required)):
    logger.info("POST /drivers/orders/{oid}/in-delivery", oid=ordem_id)
    return driver_ordem.mark_in_delivery(ordem_id=ordem_id)


@router.post("/orders/{ordem_id}/delivered")
async def mark_delivered(ordem_id: str, payload: dict = Depends(driver_required)):
    logger.info("POST /drivers/orders/{oid}/delivered", oid=ordem_id)
    return driver_ordem.mark_delivered(ordem_id=ordem_id, driver_id=payload["user_id"])


@router.get("/orders/current")
async def get_current(payload: dict = Depends(driver_required)):
    logger.info("GET /drivers/orders/current")
    return driver_ordem.get_current(driver_id=payload["user_id"])


@router.get("/orders/history")
async def get_history(payload: dict = Depends(driver_required)):
    logger.info("GET /drivers/orders/history")
    return driver_ordem.get_history(driver_id=payload["user_id"])


# ── Financeiro ──

@router.get("/earnings")
async def calc_earnings(payload: dict = Depends(driver_required)):
    logger.info("GET /drivers/earnings")
    return {"earnings": driver_ordem.calc_earnings(driver_id=payload["user_id"])}


@router.get("/balance")
async def get_balance(payload: dict = Depends(driver_required)):
    logger.info("GET /drivers/balance")
    return driver_pay.get_balance(driver_id=payload["user_id"])


@router.post("/saque")
async def saque(payload: dict = Depends(driver_required)):
    logger.info("POST /drivers/saque")
    return driver_pay.saque(driver_id=payload["user_id"])
