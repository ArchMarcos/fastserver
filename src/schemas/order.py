# Schemas de pedidos
from pydantic import BaseModel, Field


class CreateOrdemRequest(BaseModel):
    entregar_em: str = Field(..., min_length=1, max_length=255)
    obs: str = Field(default="", max_length=300)
    payment_method: str = Field(default="saldo", pattern=r"^(saldo|pix)$")


class RateRequest(BaseModel):
    score: float = Field(..., ge=1, le=5)
    comment: str = Field(default="", max_length=300)


class OrdemResponse(BaseModel):
    id: str
    client_id: str
    driver_id: str
    merchant_ids: list[str]
    sub_ordens: list[dict]
    pegar_em: list[str]
    entregar_em: str
    obs: str
    payment_method: str
    total_products: float
    total_delivery_fee: float
    total_platform_tax: float
    driver_gain: float
    total: float
    status: str
    created_at: str | None = None
    updated_at: str | None = None


class SubOrdemResponse(BaseModel):
    id: str
    ordem_id: str
    merchant_id: str
    product_id: str
    product_name: str
    quantidade: int
    acompanhamentos: dict
    delivery_fee: float
    total: float
    platform_tax: float
    status: str
    obs: str


class MerchantActionResponse(BaseModel):
    message: str
    status: str
