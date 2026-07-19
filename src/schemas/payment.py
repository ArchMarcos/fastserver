# Schemas de pagamento e financeiro
from pydantic import BaseModel, Field


class RechargeRequest(BaseModel):
    value: float = Field(..., gt=0)


class BalanceResponse(BaseModel):
    balance: float


class SaqueResponse(BaseModel):
    message: str
    transferencia_id: str
    valor: float


class TransferenciaResponse(BaseModel):
    id: str
    ordem_id: str
    de: str
    para: str
    valor: float
    tipo: str
    status: str
    created_at: str | None = None


class ComprovanteResponse(BaseModel):
    id: str
    tipo: str
    de: str
    para: str
    valor: float
    descricao: str
    created_at: str | None = None
