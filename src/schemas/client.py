# Schemas de cliente, carrinho, vitrine e favoritos
from pydantic import BaseModel, Field


# ── Carrinho ──

class CartAddRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    merchant_id: str = Field(..., min_length=1)
    quantidade: int = Field(default=1, ge=1, le=99)
    acompanhamentos: dict[str, float] = Field(default_factory=dict)
    obs: str = Field(default="", max_length=200)


class CartRemoveRequest(BaseModel):
    product_id: str = Field(..., min_length=1)


class CartQtyRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    quantidade: int = Field(..., ge=1, le=99)


class CartObsRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    obs: str = Field(default="", max_length=200)


class CartItemResponse(BaseModel):
    product_id: str
    merchant_id: str
    product_name: str
    price: float
    quantidade: int
    acompanhamentos: dict[str, float]
    obs: str
    total: float


class CartResponse(BaseModel):
    merchant_id: str
    merchant_name: str
    items: list[CartItemResponse]
    total_products: float
    total_delivery_fee: float
    total_platform_tax: float
    total: float


# ── Vitrine ──

class VitrineProductResponse(BaseModel):
    id: str
    merchant_id: str
    merchant_name: str
    name: str
    description: str
    price: float
    categoria: str
    discount: float
    is_active: bool
    images_url: list[str]
    acompanhamentos: dict[str, float]


# ── Favoritos ──

class FavoriteResponse(BaseModel):
    message: str
