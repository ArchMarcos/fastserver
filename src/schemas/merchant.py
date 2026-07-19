# Schemas de merchant e produtos
from pydantic import BaseModel, Field


class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    images: list[str] = Field(default_factory=list)
    acompanhamentos: dict[str, float] = Field(default_factory=dict)
    price: float = Field(..., gt=0)
    categoria: str = Field(default="", max_length=50)


class UpdateProductRequest(BaseModel):
    field: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class ApplyDiscountRequest(BaseModel):
    discount: float = Field(..., ge=0, le=100)


class ProductResponse(BaseModel):
    id: str
    merchant_id: str
    name: str
    description: str
    images_url: list[str]
    acompanhamentos: dict[str, float]
    price: float
    categoria: str
    is_active: bool
    discount: float
    created_at: str | None = None
    updated_at: str | None = None


class ToggleOpenResponse(BaseModel):
    message: str
    is_open: bool


class MerchantPublicResponse(BaseModel):
    id: str
    name: str
    logo_url: str
    is_open: bool
    taxa_delivery: float
    categories: list[str]
    rating: float
    opening_hours: str
    delivery_time: int
    address: str
