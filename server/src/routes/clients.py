# Rotas do cliente — FastAPI Router
from fastapi import APIRouter, Depends, Query, status
from loguru import logger

from src.schemas.client import (
    CartAddRequest,
    CartRemoveRequest,
    CartQtyRequest,
    CartObsRequest,
    FavoriteResponse,
)
from src.schemas.common import SuccessResponse
from src.middlewares.auth import client_required
from src.apps.auth import client as client_app
from src.apps.clients import vitrine as vitrine_app
from src.apps.clients import cart as cart_app
from src.apps.clients import favorites as fav_app

router = APIRouter(prefix="/clients", tags=["clients"])


# ── Perfil ──

@router.get("/profile")
async def get_profile(payload: dict = Depends(client_required)):
    logger.info("GET /clients/profile")
    return client_app.get_profile(user_id=payload["user_id"])


@router.patch("/profile", response_model=SuccessResponse)
async def update_profile(field: str, value: str, payload: dict = Depends(client_required)):
    logger.info("PATCH /clients/profile")
    return client_app.update_field(user_id=payload["user_id"], field=field, value=value)


# ── Carrinho ──

@router.get("/cart")
async def get_cart(payload: dict = Depends(client_required)):
    logger.info("GET /clients/cart")
    return cart_app.get_cart(client_id=payload["user_id"])


@router.post("/cart/add")
async def add_to_cart(body: CartAddRequest, payload: dict = Depends(client_required)):
    logger.info("POST /clients/cart/add")
    return cart_app.add_to_cart(
        client_id=payload["user_id"],
        product_id=body.product_id,
        merchant_id=body.merchant_id,
        quantidade=body.quantidade,
        acompanhamentos=body.acompanhamentos,
        obs=body.obs,
    )


@router.post("/cart/remove")
async def remove_from_cart(body: CartRemoveRequest, payload: dict = Depends(client_required)):
    logger.info("POST /clients/cart/remove")
    return cart_app.remove_from_cart(client_id=payload["user_id"], product_id=body.product_id)


@router.patch("/cart/qty")
async def update_qty(body: CartQtyRequest, payload: dict = Depends(client_required)):
    logger.info("PATCH /clients/cart/qty")
    return cart_app.update_quantity(client_id=payload["user_id"], product_id=body.product_id, quantidade=body.quantidade)


@router.patch("/cart/obs")
async def update_obs(body: CartObsRequest, payload: dict = Depends(client_required)):
    logger.info("PATCH /clients/cart/obs")
    return cart_app.update_obs(client_id=payload["user_id"], product_id=body.product_id, obs=body.obs)


@router.post("/cart/clear")
async def clear_cart(payload: dict = Depends(client_required)):
    logger.info("POST /clients/cart/clear")
    return cart_app.clear_cart(client_id=payload["user_id"])


@router.get("/cart/totals")
async def calc_totals(payload: dict = Depends(client_required)):
    logger.info("GET /clients/cart/totals")
    return cart_app.calc_cart_totals(client_id=payload["user_id"])


# ── Vitrine ──

@router.get("/vitrine/categories")
async def list_categories(payload: dict = Depends(client_required)):
    logger.info("GET /clients/vitrine/categories")
    return vitrine_app.list_categories()


@router.get("/vitrine/category/{categoria}")
async def list_by_category(categoria: str, payload: dict = Depends(client_required)):
    logger.info("GET /clients/vitrine/category/{cat}", cat=categoria)
    return vitrine_app.list_by_category(categoria=categoria)


@router.get("/vitrine/search")
async def search_vitrine(query: str = Query(..., min_length=1), payload: dict = Depends(client_required)):
    logger.info("GET /clients/vitrine/search?q={q}", q=query)
    return vitrine_app.search(query=query)


@router.get("/vitrine/merchant/{merchant_id}")
async def list_by_merchant(merchant_id: str, payload: dict = Depends(client_required)):
    logger.info("GET /clients/vitrine/merchant/{mid}", mid=merchant_id)
    return vitrine_app.list_by_merchant(merchant_id=merchant_id)


@router.get("/vitrine/open")
async def list_open_merchants(payload: dict = Depends(client_required)):
    logger.info("GET /clients/vitrine/open")
    return vitrine_app.list_open_merchants()


@router.get("/vitrine/product/{product_id}")
async def get_product(product_id: str, payload: dict = Depends(client_required)):
    logger.info("GET /clients/vitrine/product/{pid}", pid=product_id)
    return vitrine_app.get_product(product_id=product_id)


# ── Favoritos ──

@router.get("/favorites")
async def get_favorites(payload: dict = Depends(client_required)):
    logger.info("GET /clients/favorites")
    return fav_app.list_favorites(client_id=payload["user_id"])


@router.post("/favorites/{merchant_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(merchant_id: str, payload: dict = Depends(client_required)):
    logger.info("POST /clients/favorites/{mid}", mid=merchant_id)
    return fav_app.add_favorite(client_id=payload["user_id"], merchant_id=merchant_id)


@router.delete("/favorites/{merchant_id}", response_model=FavoriteResponse)
async def remove_favorite(merchant_id: str, payload: dict = Depends(client_required)):
    logger.info("DELETE /clients/favorites/{mid}", mid=merchant_id)
    return fav_app.remove_favorite(client_id=payload["user_id"], merchant_id=merchant_id)
