# Pagamentos do cliente — recarga, pagamento, saldo, comprovantes
from loguru import logger

from src.database.database import clients, merchants, ordens, transferencias, recargas, comprovantes
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, ValidationError, PaymentError
from src.apps.notifications import email as email_notif, in_app as in_app_notif


def recharge(client_id, value):
    logger.info("recarga: {cid} valor: {val}", cid=client_id, val=value)

    client_data = clients.get(client_id)
    if not client_data:
        raise NotFoundError("Cliente não encontrado")
    client_data = deserialize(client_data)

    rec = recargas.create(
        user_id=client_id,
        valor=value,
        metodo="pix",
        status="confirmada",
    )

    new_balance = float(client_data.get("balance", 0)) + value
    clients.update({"balance": new_balance}, id=client_id)

    comprovantes.create(
        recarga_id=str(rec["id"]),
        tipo="recarga",
        de="",
        para=client_id,
        valor=value,
        descricao=f"Recarga de R$ {value:.2f} via PIX",
    )

    return {"message": f"Recarga de R$ {value:.2f} confirmada", "balance": new_balance}


def pagar_ordem(ordem_id, client_id):
    logger.info("pagar ordem: {oid} cliente: {cid}", oid=ordem_id, cid=client_id)

    o = ordens.get(ordem_id)
    if not o:
        raise NotFoundError("Ordem não encontrada")
    o = deserialize(o)

    if o.get("status") != "pendente":
        raise ValidationError("Ordem não está pendente de pagamento")
    if str(o.get("client_id")) != str(client_id):
        raise ValidationError("Esta ordem não pertence a este cliente")

    total = float(o.get("total", 0))
    client_data = clients.get(client_id)
    if not client_data:
        raise NotFoundError("Cliente não encontrado")
    client_data = deserialize(client_data)

    balance = float(client_data.get("balance", 0))
    if balance < total:
        raise PaymentError(f"Saldo insuficiente. Disponível: R$ {balance:.2f}, necessário: R$ {total:.2f}")

    new_balance = round(balance - total, 2)
    clients.update({"balance": new_balance}, id=client_id)

    merchant_count = len(o.get("merchant_ids", [1]))
    for mid in o.get("merchant_ids", []):
        merchant_valor = round((total - float(o.get("total_platform_tax", 0))) / merchant_count, 2)
        t = transferencias.create(
            ordem_id=ordem_id,
            de=client_id,
            para=mid,
            valor=merchant_valor,
            tipo="ordem",
            status="confirmada",
        )
        comprovantes.create(
            transferencia_id=str(t["id"]),
            tipo="pagamento_ordem",
            de=client_id,
            para=mid,
            valor=merchant_valor,
            descricao=f"Pagamento ordem #{ordem_id}",
        )

        # Adiciona saldo ao merchant
        m = merchants.get(mid)
        if m:
            m = deserialize(m)
            merchants.update({"balance": float(m.get("balance", 0)) + merchant_valor}, id=mid)

    platform_tax = float(o.get("total_platform_tax", 0))
    if platform_tax > 0:
        t = transferencias.create(
            ordem_id=ordem_id,
            de="plataforma",
            para="plataforma",
            valor=platform_tax,
            tipo="platform_tax",
            status="confirmada",
        )
        comprovantes.create(
            transferencia_id=str(t["id"]),
            tipo="platform_tax",
            de=client_id,
            para="plataforma",
            valor=platform_tax,
            descricao=f"Taxa da plataforma ordem #{ordem_id}",
        )

    ordens.update({"status": "aceito"}, id=ordem_id)

    in_app_notif.send(client_id, "client", "Pagamento confirmado", f"Pedido #{ordem_id} pago. Total: R$ {total:.2f}")
    for mid in o.get("merchant_ids", []):
        in_app_notif.send(mid, "merchant", "Novo pedido!", f"Ordem #{ordem_id} com valor de R$ {total:.2f}")

    return {"message": "Pagamento confirmado", "balance": new_balance, "status": "aceito"}


def get_balance(client_id):
    client_data = clients.get(client_id)
    if not client_data:
        raise NotFoundError("Cliente não encontrado")
    return {"balance": float(deserialize(client_data).get("balance", 0))}


def get_history(client_id):
    transfers = transferencias.find(de=client_id)
    recharges = recargas.find(user_id=client_id)
    items = []
    for t in transfers:
        t = deserialize(t)
        items.append({"tipo": "transferencia", **t})
    for r in recharges:
        r = deserialize(r)
        items.append({"tipo": "recarga", **r})
    items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
    return items


def get_comprovante_by_transfer(transferencia_id):
    c = comprovantes.get(transferencia_id)
    if not c:
        raise NotFoundError("Comprovante não encontrado")
    return deserialize(c)


def get_comprovante_by_recharge(recarga_id):
    c = comprovantes.get(recarga_id)
    if not c:
        raise NotFoundError("Comprovante não encontrado")
    return deserialize(c)


def list_comprovantes(client_id):
    all_c = comprovantes.find()
    result = []
    for c in all_c:
        c = deserialize(c)
        if c.get("de") == client_id or c.get("para") == client_id:
            result.append(c)
    return result
