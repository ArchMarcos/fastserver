# Rotas do merchant — FastAPI Router
from fastapi import APIRouter, Depends, status
from loguru import logger

from src.schemas.merchant import (
    CreateProductRequest,
    UpdateProductRequest,
    ApplyDiscountRequest,
    ProductResponse,
    ToggleOpenResponse,
)
from src.schemas.common import SuccessResponse
from src.middlewares.auth import merchant_required
from src.apps.auth import merchant as merchant_app
from src.apps.merchant import products as products_app

router = APIRouter(prefix="/merchants", tags=["merchants"])


# ── Perfil ──

@router.get("/profile")
async def get_profile(payload: dict = Depends(merchant_required)):
    logger.info("GET /merchants/profile")
    return merchant_app.get_profile(user_id=payload["user_id"])


@router.patch("/profile", response_model=SuccessResponse)
async def update_profile(field: str, value: str, payload: dict = Depends(merchant_required)):
    logger.info("PATCH /merchants/profile")
    return merchant_app.update_field(user_id=payload["user_id"], field=field, value=value)


@router.post("/toggle-open", response_model=ToggleOpenResponse)
async def toggle_open(payload: dict = Depends(merchant_required)):
    logger.info("POST /merchants/toggle-open")
    return merchant_app.toggle_open(merchant_id=payload["user_id"])


# ── Produtos ──

@router.get("/products", response_model=list[ProductResponse])
async def list_products(payload: dict = Depends(merchant_required)):
    logger.info("GET /merchants/products")
    return products_app.list_my_products(merchant_id=payload["user_id"])


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(body: CreateProductRequest, payload: dict = Depends(merchant_required)):
    logger.info("POST /merchants/products")
    return products_app.new_product(
        merchant_id=payload["user_id"],
        name=body.name,
        description=body.description,
        images=body.images,
        acompanhamentos=body.acompanhamentos,
        price=body.price,
        categoria=body.categoria,
    )


@router.patch("/products/{product_id}", response_model=SuccessResponse)
async def update_product(product_id: str, body: UpdateProductRequest, payload: dict = Depends(merchant_required)):
    logger.info("PATCH /merchants/products/{pid}", pid=product_id)
    return products_app.update_product(product_id=product_id, field=body.field, value=body.value)


@router.delete("/products/{product_id}", response_model=SuccessResponse)
async def remove_product(product_id: str, payload: dict = Depends(merchant_required)):
    logger.info("DELETE /merchants/products/{pid}", pid=product_id)
    return products_app.remove_product(product_id=product_id)


@router.patch("/products/{product_id}/toggle", response_model=SuccessResponse)
async def toggle_product(product_id: str, payload: dict = Depends(merchant_required)):
    logger.info("PATCH /merchants/products/{pid}/toggle", pid=product_id)
    return products_app.toggle_active(product_id=product_id)


@router.patch("/products/{product_id}/discount", response_model=SuccessResponse)
async def apply_discount(product_id: str, body: ApplyDiscountRequest, payload: dict = Depends(merchant_required)):
    logger.info("PATCH /merchants/products/{pid}/discount", pid=product_id)
    return products_app.apply_discount(product_id=product_id, discount=body.discount)
