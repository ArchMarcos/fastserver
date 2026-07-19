# Gestão de pedidos do merchant — ciclo de vida de sub-ordens
from loguru import logger

from src.database.database import ordens, sub_ordens
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, ValidationError
from src.apps.notifications import in_app as in_app_notif

_TRANSITIONS = {
    "pendente": {"aceito", "recusado"},
    "aceito": {"preparando"},
    "preparando": {"pronto"},
    "pronto": {"esperando_entregador"},
    "esperando_entregador": {"coletado"},
    "coletado": {"em_entrega"},
    "em_entrega": {"entregue"},
}


def _transition(sub_ordem_id, novo_status):
    """Valida e executa transição de status de uma sub-ordem."""
    sub = sub_ordens.get(sub_ordem_id)
    if not sub:
        raise NotFoundError("Sub-ordem não encontrada")
    sub = deserialize(sub)

    current = sub.get("status", "")
    allowed = _TRANSITIONS.get(current, set())
    if novo_status not in allowed:
        raise ValidationError(f"Transição inválida: {current} → {novo_status}")

    sub_ordens.update({"status": novo_status}, id=sub_ordem_id)

    # Sincroniza OrdemCart se aplicável
    ordem_id = sub.get("ordem_id", "")
    if ordem_id and novo_status in ("aceito", "recusado", "esperando_entregador", "coletado", "entregue"):
        _sync_ordem_status(ordem_id)

    # Notifica cliente sobre mudança de status
    if ordem_id:
        o = ordens.get(ordem_id)
        if o:
            o = deserialize(o)
            client_id = o.get("client_id", "")
            if client_id:
                in_app_notif.send(client_id, "client", "Atualização do pedido", f"Seu pedido #{ordem_id} está {novo_status}")

    return {"message": f"Sub-ordem {novo_status}", "status": novo_status}


def _sync_ordem_status(ordem_id):
    """Avança o status da OrdemCart com base no status das sub-ordens."""
    o = ordens.get(ordem_id)
    if not o:
        return
    o = deserialize(o)

    subs = sub_ordens.find(ordem_id=ordem_id)
    statuses = {deserialize(s).get("status", "") for s in subs}

    if statuses == {"aceito"}:
        ordens.update({"status": "aceito"}, id=ordem_id)
    elif "recusado" in statuses:
        ordens.update({"status": "cancelado"}, id=ordem_id)
    elif "esperando_entregador" in statuses:
        ordens.update({"status": "esperando_entregador"}, id=ordem_id)
    elif "coletado" in statuses:
        ordens.update({"status": "coletado"}, id=ordem_id)
    elif statuses == {"entregue"}:
        ordens.update({"status": "entregue"}, id=ordem_id)


def list_pending(merchant_id):
    return _find_sub_ordens(merchant_id=merchant_id, status="pendente")


def list_all(merchant_id):
    return _find_sub_ordens(merchant_id=merchant_id)


def list_active(merchant_id):
    active = {"pendente", "aceito", "preparando", "pronto", "esperando_entregador", "coletado", "em_entrega"}
    return _find_sub_ordens(merchant_id=merchant_id, filtro=lambda s: s.get("status") in active)


def list_history(merchant_id):
    final = {"entregue", "recusado", "cancelado"}
    return _find_sub_ordens(merchant_id=merchant_id, filtro=lambda s: s.get("status") in final)


def _find_sub_ordens(merchant_id=None, status=None, filtro=None):
    if merchant_id:
        all_subs = sub_ordens.find(merchant_id=merchant_id)
    else:
        all_subs = []
    result = []
    for s in all_subs:
        s = deserialize(s)
        if status and s.get("status") != status:
            continue
        if filtro and not filtro(s):
            continue
        result.append(_build_sub_response(s))
    return result


def get_sub_ordem(sub_ordem_id):
    s = sub_ordens.get(sub_ordem_id)
    if not s:
        raise NotFoundError("Sub-ordem não encontrada")
    return _build_sub_response(deserialize(s))


def accept(sub_ordem_id):
    logger.info("aceitar sub-ordem: {sid}", sid=sub_ordem_id)
    return _transition(sub_ordem_id, "aceito")


def refuse(sub_ordem_id):
    logger.info("recusar sub-ordem: {sid}", sid=sub_ordem_id)
    return _transition(sub_ordem_id, "recusado")


def start_preparing(sub_ordem_id):
    logger.info("iniciar preparo: {sid}", sid=sub_ordem_id)
    return _transition(sub_ordem_id, "preparando")


def mark_ready(sub_ordem_id):
    logger.info("marcar pronto: {sid}", sid=sub_ordem_id)
    return _transition(sub_ordem_id, "pronto")


def waiting_driver(sub_ordem_id):
    logger.info("aguardando entregador: {sid}", sid=sub_ordem_id)
    return _transition(sub_ordem_id, "esperando_entregador")


def mark_collected(sub_ordem_id):
    logger.info("coletado: {sid}", sid=sub_ordem_id)
    return _transition(sub_ordem_id, "coletado")


def list_ordens(merchant_id):
    all_ordens = ordens.find()
    result = []
    for o in all_ordens:
        o = deserialize(o)
        if merchant_id in o.get("merchant_ids", []):
            result.append(_build_ordem_response(o))
    return result


def get_ordem(ordem_id):
    o = ordens.get(ordem_id)
    if not o:
        raise NotFoundError("Ordem não encontrada")
    return _build_ordem_response(deserialize(o))


def calc_earnings(merchant_id):
    subs = sub_ordens.find(merchant_id=merchant_id, status="entregue")
    total = sum(float(deserialize(s).get("total", 0)) for s in subs)
    return total


def _build_sub_response(s):
    return {
        "id": str(s.get("id", "")),
        "ordem_id": str(s.get("ordem_id", "")),
        "merchant_id": str(s.get("merchant_id", "")),
        "product_id": s.get("product_id", ""),
        "product_name": s.get("product_name", ""),
        "quantidade": int(s.get("quantidade", 1)),
        "acompanhamentos": s.get("acompanhamentos", {}),
        "delivery_fee": float(s.get("delivery_fee", 0)),
        "total": float(s.get("total", 0)),
        "platform_tax": float(s.get("platform_tax", 0)),
        "status": s.get("status", ""),
        "obs": s.get("obs", ""),
    }


def _build_ordem_response(o):
    return {
        "id": str(o.get("id", "")),
        "client_id": str(o.get("client_id", "")),
        "driver_id": str(o.get("driver_id", "")),
        "merchant_ids": o.get("merchant_ids", []),
        "total_products": float(o.get("total_products", 0)),
        "total_delivery_fee": float(o.get("total_delivery_fee", 0)),
        "total": float(o.get("total", 0)),
        "status": o.get("status", ""),
    }
