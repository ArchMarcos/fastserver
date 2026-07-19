# Rotas de notificações — in-app
from fastapi import APIRouter, Depends
from loguru import logger

from src.schemas.common import SuccessResponse
from src.middlewares.auth import auth_required
from src.apps.notifications import in_app as in_app_notif

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(payload: dict = Depends(auth_required)):
    logger.info("GET /notifications")
    return in_app_notif.list_by_user(user_id=payload["user_id"], role=payload["role"])


@router.post("/clear", response_model=SuccessResponse)
async def clear_notifications(payload: dict = Depends(auth_required)):
    logger.info("POST /notifications/clear")
    return in_app_notif.clear(user_id=payload["user_id"], role=payload["role"])
