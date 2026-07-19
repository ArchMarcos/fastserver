# Pedidos do cliente — criação, listagem, cancelamento, avaliação
from loguru import logger

from src.database.database import ordens, sub_ordens, clients, merchants, ratings
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, ValidationError
from src.apps.notifications import in_app as in_app_notif

CANCELAVEIS = ["pendente", "aceito", "preparando", "pronto", "esperando_entregador"]


def create_ordem(client_id, entregar_em, obs="", payment_method="saldo"):
    logger.info("criar ordem: {cid}", cid=client_id)

    client_data = clients.get(client_id)
    if not client_data:
        raise NotFoundError("Cliente não encontrado")
    client_data = deserialize(client_data)

    cart = client_data.get("cart", [])
    if not cart:
        raise ValidationError("Carrinho vazio")

    merchant_items: dict[str, list] = {}
    for item in cart:
        mid = item.get("merchant_id")
        if mid not in merchant_items:
            merchant_items[mid] = []
        merchant_items[mid].append(item)

    merchant_ids = list(merchant_items.keys())
    pegar_em = []
    sub_ordem_list = []
    total_products = 0.0
    total_delivery_fee = 0.0

    for mid in merchant_ids:
        m = merchants.get(mid)
        if not m:
            raise NotFoundError(f"Merchant {mid} não encontrado")
        m = deserialize(m)
        pegar_em.append(m.get("address", ""))
        delivery_fee = float(m.get("taxa_delivery", 0))
        total_delivery_fee += delivery_fee

        for item in merchant_items[mid]:
            subtotal = float(item.get("total", 0))
            total_products += subtotal
            sub_ordem_list.append({
                "merchant_id": mid,
                "product_id": item.get("product_id", ""),
                "product_name": item.get("product_name", ""),
                "quantidade": int(item.get("quantidade", 1)),
                "acompanhamentos": item.get("acompanhamentos", {}),
                "delivery_fee": delivery_fee,
                "total": subtotal,
                "platform_tax": round(subtotal * 0.05, 2),
                "status": "pendente",
                "obs": item.get("obs", ""),
            })

    total_platform_tax = round(total_products * 0.05, 2)
    total = round(total_products + total_delivery_fee + total_platform_tax, 2)

    ordem_data = {
        "client_id": client_id,
        "driver_id": "",
        "merchant_ids": merchant_ids,
        "sub_ordens": [],
        "pegar_em": pegar_em,
        "entregar_em": entregar_em,
        "obs": obs,
        "payment_method": payment_method,
        "total_products": total_products,
        "total_delivery_fee": total_delivery_fee,
        "total_platform_tax": total_platform_tax,
        "driver_gain": 0.0,
        "total": total,
        "status": "pendente",
    }

    created_ordem = ordens.create(**serialize(ordem_data))
    ordem_id = str(created_ordem["id"])

    for sub in sub_ordem_list:
        sub["ordem_id"] = ordem_id
        sub_ordens.create(**serialize(sub))

    existing_ordens = client_data.get("ordem", [])
    existing_ordens.append(ordem_id)
    clients.update(serialize({
        "ordem": existing_ordens,
        "active_ordem": ordem_id,
        "cart": [],
    }), id=client_id)

    in_app_notif.send(client_id, "client", "Pedido criado", f"Pedido #{ordem_id} criado com sucesso. Total: R$ {total:.2f}")

    return _build_ordem_response(created_ordem)


def list_ordens(client_id):
    logger.info("listar ordens: {cid}", cid=client_id)
    return _find_ordens(client_id=client_id)


def list_ordens_active(client_id):
    logger.info("ordens ativas: {cid}", cid=client_id)
    active = {"pendente", "aceito", "preparando", "em_coleta", "esperando_entregador", "coletado", "em_entrega"}
    return _find_ordens(client_id=client_id, filtro=lambda o: o.get("status") in active)


def list_ordens_history(client_id):
    logger.info("ordens histórico: {cid}", cid=client_id)
    final = {"entregue", "cancelado"}
    return _find_ordens(client_id=client_id, filtro=lambda o: o.get("status") in final)


def _find_ordens(client_id=None, filtro=None):
    all_ordens = ordens.find(client_id=client_id) if client_id else []
    result = []
    for o in all_ordens:
        o = deserialize(o)
        if filtro and not filtro(o):
            continue
        result.append(_build_ordem_response(o))
    return result


def get_ordem(ordem_id):
    logger.info("get ordem: {oid}", oid=ordem_id)
    o = ordens.get(ordem_id)
    if not o:
        raise NotFoundError("Ordem não encontrada")
    o = deserialize(o)
    return _build_ordem_response(o)


def cancel_ordem(ordem_id, client_id=None):
    logger.info("cancelar ordem: {oid}", oid=ordem_id)

    o = ordens.get(ordem_id)
    if not o:
        raise NotFoundError("Ordem não encontrada")
    o = deserialize(o)

    if o.get("status") not in CANCELAVEIS:
        raise ValidationError("Não é possível cancelar após a coleta do entregador")

    if client_id and str(o.get("client_id")) != str(client_id):
        raise ValidationError("Você não pode cancelar uma ordem de outro cliente")

    ordens.update({"status": "cancelado"}, id=ordem_id)
    return {"message": "Ordem cancelada com sucesso", "status": "cancelado"}


def rate_ordem(ordem_id, score, comment=""):
    logger.info("avaliar ordem: {oid} score: {s}", oid=ordem_id, s=score)

    o = ordens.get(ordem_id)
    if not o:
        raise NotFoundError("Ordem não encontrada")
    o = deserialize(o)

    if o.get("status") != "entregue":
        raise ValidationError("Só é possível avaliar ordens entregues")

    ratings.create(
        ordem_id=ordem_id,
        user_id=str(o.get("client_id", "")),
        score=score,
        comment=comment,
    )

    return {"message": "Avaliação registrada com sucesso"}


def _build_ordem_response(o):
    return {
        "id": str(o.get("id", "")),
        "client_id": str(o.get("client_id", "")),
        "driver_id": str(o.get("driver_id", "")),
        "merchant_ids": o.get("merchant_ids", []),
        "sub_ordens": o.get("sub_ordens", []),
        "pegar_em": o.get("pegar_em", []),
        "entregar_em": o.get("entregar_em", ""),
        "obs": o.get("obs", ""),
        "payment_method": o.get("payment_method", ""),
        "total_products": float(o.get("total_products", 0)),
        "total_delivery_fee": float(o.get("total_delivery_fee", 0)),
        "total_platform_tax": float(o.get("total_platform_tax", 0)),
        "driver_gain": float(o.get("driver_gain", 0)),
        "total": float(o.get("total", 0)),
        "status": o.get("status", ""),
        "created_at": str(o.get("created_at", "")),
        "updated_at": str(o.get("updated_at", "")),
    }
