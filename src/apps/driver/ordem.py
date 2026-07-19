# Pedidos do entregador — aceitar, coletar, entregar, histórico
from loguru import logger

from src.database.database import ordens, sub_ordens, drivers, driver_history
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, ValidationError
from src.apps.notifications import in_app as in_app_notif


def list_available(driver_id):
    """Lista ordens aguardando entregador."""
    all_ordens = ordens.find(status="esperando_entregador")
    result = []
    for o in all_ordens:
        o = deserialize(o)
        if not o.get("driver_id"):
            result.append(_build_ordem_minimal(o))
    return result


def accept_order(driver_id, ordem_id):
    logger.info("entregador aceitou: {did} ordem: {oid}", did=driver_id, oid=ordem_id)

    o = ordens.get(ordem_id)
    if not o:
        raise NotFoundError("Ordem não encontrada")
    o = deserialize(o)

    if o.get("status") != "esperando_entregador":
        raise ValidationError("Ordem não está aguardando entregador")
    if o.get("driver_id"):
        raise ValidationError("Ordem já possui um entregador")

    ordens.update({"driver_id": driver_id, "status": "coletado"}, id=ordem_id)

    # Atualiza status das sub-ordens
    subs = sub_ordens.find(ordem_id=ordem_id)
    for s in subs:
        s = deserialize(s)
        if s.get("status") == "esperando_entregador":
            sub_ordens.update({"status": "coletado"}, id=s["id"])

    drivers.update({"current_ordem": ordem_id}, id=driver_id)
    return {"message": "Ordem aceita", "status": "coletado"}


def mark_in_delivery(ordem_id):
    logger.info("saiu para entrega: {oid}", oid=ordem_id)
    return _transition_ordem(ordem_id, "coletado", "em_entrega")


def mark_delivered(ordem_id, driver_id=None):
    logger.info("entregue: {oid}", oid=ordem_id)

    o = ordens.get(ordem_id)
    if not o:
        raise NotFoundError("Ordem não encontrada")
    o = deserialize(o)

    if o.get("status") != "em_entrega":
        raise ValidationError("Ordem não está em entrega")

    ordens.update({"status": "entregue"}, id=ordem_id)

    # Atualiza sub-ordens
    subs = sub_ordens.find(ordem_id=ordem_id)
    for s in subs:
        s = deserialize(s)
        if s.get("status") in ("coletado", "em_entrega"):
            sub_ordens.update({"status": "entregue"}, id=s["id"])

    # Registra no histórico do driver
    actual_driver = driver_id or o.get("driver_id", "")
    if actual_driver:
        driver_history.create(
            driver_id=actual_driver,
            ordem_id=ordem_id,
            status="entregue",
        )
        drivers.update({"current_ordem": ""}, id=actual_driver)

    # Notifica cliente
    client_id = o.get("client_id", "")
    if client_id:
        in_app_notif.send(client_id, "client", "Pedido entregue!", f"Seu pedido #{ordem_id} foi entregue. Bom apetite!")

    return {"message": "Pedido entregue com sucesso", "status": "entregue"}


def reject_order(driver_id, ordem_id):
    logger.info("entregador recusou: {did} ordem: {oid}", did=driver_id, oid=ordem_id)
    return {"message": "Ordem recusada"}


def _transition_ordem(ordem_id, from_status, to_status):
    o = ordens.get(ordem_id)
    if not o:
        raise NotFoundError("Ordem não encontrada")
    o = deserialize(o)
    if o.get("status") != from_status:
        raise ValidationError(f"Status inválido: {o.get('status')}, esperado: {from_status}")
    ordens.update({"status": to_status}, id=ordem_id)
    return {"message": f"Ordem {to_status}", "status": to_status}


def get_current(driver_id):
    d = drivers.get(driver_id)
    if not d:
        raise NotFoundError("Entregador não encontrado")
    d = deserialize(d)
    current = d.get("current_ordem", "")
    if not current:
        return {}
    o = ordens.get(current)
    if not o:
        return {}
    return _build_ordem_minimal(deserialize(o))


def get_history(driver_id):
    all_h = driver_history.find(driver_id=driver_id)
    return [deserialize(h) for h in all_h]


def calc_earnings(driver_id):
    all_h = driver_history.find(driver_id=driver_id, status="entregue")
    total = 0.0
    for h in all_h:
        h = deserialize(h)
        o = ordens.get(h.get("ordem_id", ""))
        if o:
            o = deserialize(o)
            total += float(o.get("total_delivery_fee", 0))
    return total


def _build_ordem_minimal(o):
    return {
        "id": str(o.get("id", "")),
        "client_id": str(o.get("client_id", "")),
        "merchant_ids": o.get("merchant_ids", []),
        "pegar_em": o.get("pegar_em", []),
        "entregar_em": o.get("entregar_em", ""),
        "total": float(o.get("total", 0)),
        "total_delivery_fee": float(o.get("total_delivery_fee", 0)),
        "status": o.get("status", ""),
    }
