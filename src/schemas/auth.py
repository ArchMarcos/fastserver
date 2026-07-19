# Schemas de autenticação — request/response
from pydantic import BaseModel, Field


class RegisterClientRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    phone: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    address: str = Field(..., min_length=3, max_length=255)


class RegisterMerchantRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    phone: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    address: str = Field(..., min_length=3, max_length=255)
    logo_url: str = ""
    opening_hours: str = ""


class RegisterDriverRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    phone: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    address: str = Field(..., min_length=3, max_length=255)
    veiculo: str = Field(default="moto", pattern=r"^(moto|bicycle|car)?$")


class LoginRequest(BaseModel):
    ident: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class ConfirmEmailRequest(BaseModel):
    token: str = Field(..., min_length=1)


class RegisterResponse(BaseModel):
    message: str
    user_id: str
    email_token: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str
