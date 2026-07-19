# Favoritos do cliente — gerenciamento de merchants favoritos
from loguru import logger

from src.database.database import clients, merchants
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, ValidationError


def list_favorites(client_id):
    logger.info("listar favoritos: {cid}", cid=client_id)

    client_data = clients.get(client_id)
    if not client_data:
        raise NotFoundError("Cliente não encontrado")

    client_data = deserialize(client_data)
    fav_ids = client_data.get("favorites", [])

    result = []
    for mid in fav_ids:
        m = merchants.get(mid)
        if m:
            m = deserialize(m)
            result.append({
                "id": str(m["id"]),
                "name": m.get("name", ""),
                "logo_url": m.get("logo_url", ""),
                "is_open": m.get("is_open", False),
                "taxa_delivery": float(m.get("taxa_delivery", 0)),
                "categories": m.get("categories", []),
                "rating": float(m.get("rating", 0)),
                "delivery_time": int(m.get("delivery_time", 30)),
                "address": m.get("address", ""),
            })

    return result


def add_favorite(client_id, merchant_id):
    logger.info("add favorito: {cid} merchant: {mid}", cid=client_id, mid=merchant_id)

    # Verifica se merchant existe
    merchant_data = merchants.get(merchant_id)
    if not merchant_data:
        raise NotFoundError("Merchant não encontrado")

    client_data = clients.get(client_id)
    if not client_data:
        raise NotFoundError("Cliente não encontrado")

    client_data = deserialize(client_data)
    favorites = client_data.get("favorites", [])

    if merchant_id in favorites:
        raise ValidationError("Merchant já está nos favoritos")

    favorites.append(merchant_id)
    clients.update(serialize({"favorites": favorites}), id=client_id)

    return {"message": "Favorito adicionado com sucesso"}


def remove_favorite(client_id, merchant_id):
    logger.info("remove favorito: {cid} merchant: {mid}", cid=client_id, mid=merchant_id)

    client_data = clients.get(client_id)
    if not client_data:
        raise NotFoundError("Cliente não encontrado")

    client_data = deserialize(client_data)
    favorites = client_data.get("favorites", [])

    if merchant_id not in favorites:
        raise NotFoundError("Merchant não está nos favoritos")

    favorites = [f for f in favorites if f != merchant_id]
    clients.update(serialize({"favorites": favorites}), id=client_id)

    return {"message": "Favorito removido com sucesso"}


def is_favorite(client_id, merchant_id):
    client_data = clients.get(client_id)
    if not client_data:
        return False

    client_data = deserialize(client_data)
    return merchant_id in client_data.get("favorites", [])
