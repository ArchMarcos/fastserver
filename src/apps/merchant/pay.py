# Finanças do merchant — saque, balanço, líquido, comprovantes
from loguru import logger

from src.database.database import merchants, transferencias, comprovantes
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, PaymentError


def saque(merchant_id):
    logger.info("saque merchant: {mid}", mid=merchant_id)

    m = merchants.get(merchant_id)
    if not m:
        raise NotFoundError("Merchant não encontrado")
    m = deserialize(m)

    balance = float(m.get("balance", 0))
    if balance <= 0:
        raise PaymentError("Saldo insuficiente para saque")

    t = transferencias.create(
        de=merchant_id,
        para=merchant_id,
        valor=balance,
        tipo="saque",
        status="confirmada",
    )

    merchants.update({"balance": 0.0}, id=merchant_id)

    return {
        "message": f"Saque de R$ {balance:.2f} realizado via PIX",
        "transferencia_id": str(t["id"]),
        "valor": balance,
    }


def get_balance(merchant_id):
    m = merchants.get(merchant_id)
    if not m:
        raise NotFoundError("Merchant não encontrado")
    return {"balance": float(deserialize(m).get("balance", 0))}


def get_history(merchant_id):
    all_t = transferencias.find(de=merchant_id)
    return [deserialize(t) for t in all_t]


def calc_liquid(merchant_id):
    """Calcula valor líquido (recebido - taxa)."""
    all_t = transferencias.find(de=merchant_id)
    received = 0.0
    paid = 0.0
    for t in all_t:
        t = deserialize(t)
        if t.get("tipo") == "ordem":
            received += float(t.get("valor", 0))
        elif t.get("tipo") == "platform_tax":
            paid += float(t.get("valor", 0))
    return round(received - paid, 2)


def get_comprovante_by_transfer(transferencia_id):
    c = comprovantes.get(transferencia_id)
    if not c:
        raise NotFoundError("Comprovante não encontrado")
    return deserialize(c)


def list_comprovantes(merchant_id):
    all_c = comprovantes.find()
    return [deserialize(c) for c in all_c if deserialize(c).get("de") == merchant_id]
