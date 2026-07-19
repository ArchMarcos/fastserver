# Finanças do entregador — saldo, saque, comprovantes
from loguru import logger

from src.database.database import drivers, transferencias, comprovantes
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, PaymentError


def get_balance(driver_id):
    d = drivers.get(driver_id)
    if not d:
        raise NotFoundError("Entregador não encontrado")
    return {"balance": float(deserialize(d).get("balance", 0))}


def saque(driver_id):
    logger.info("saque driver: {did}", did=driver_id)

    d = drivers.get(driver_id)
    if not d:
        raise NotFoundError("Entregador não encontrado")
    d = deserialize(d)

    balance = float(d.get("balance", 0))
    if balance <= 0:
        raise PaymentError("Saldo insuficiente para saque")

    t = transferencias.create(
        de=driver_id,
        para=driver_id,
        valor=balance,
        tipo="saque",
        status="confirmada",
    )

    drivers.update({"balance": 0.0}, id=driver_id)

    return {
        "message": f"Saque de R$ {balance:.2f} realizado via PIX",
        "transferencia_id": str(t["id"]),
        "valor": balance,
    }


def get_history(driver_id):
    all_t = transferencias.find(de=driver_id)
    return [deserialize(t) for t in all_t]


def get_comprovante_by_transfer(transferencia_id):
    c = comprovantes.get(transferencia_id)
    if not c:
        raise NotFoundError("Comprovante não encontrado")
    return deserialize(c)


def list_comprovantes(driver_id):
    all_c = comprovantes.find()
    return [deserialize(c) for c in all_c if deserialize(c).get("de") == driver_id]
