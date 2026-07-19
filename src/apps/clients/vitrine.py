# Vitrine do cliente — busca e listagem de produtos
from loguru import logger

from src.database.database import products, merchants
from src.database.database import deserialize
from src.infra.errors import NotFoundError


def _enrich_product(p):
    """Converte produto bruto + adiciona merchant_name."""
    p = deserialize(p)
    merchant_data = merchants.get(str(p["merchant_id"]))
    merchant_name = "Desconhecido"
    if merchant_data:
        merchant_data = deserialize(merchant_data)
        merchant_name = merchant_data.get("name", "Desconhecido")

    return {
        "id": str(p["id"]),
        "merchant_id": str(p["merchant_id"]),
        "merchant_name": merchant_name,
        "name": p["name"],
        "description": p.get("description", ""),
        "price": float(p["price"]),
        "categoria": p.get("categoria", ""),
        "discount": float(p.get("discount", 0)),
        "is_active": p.get("is_active", True),
        "images_url": p.get("images_url", []),
        "acompanhamentos": p.get("acompanhamentos", {}),
    }


def list_by_category(categoria):
    logger.info("vitrine por categoria: {cat}", cat=categoria)

    all_products = products.find(categoria=categoria, is_active=True)
    return [_enrich_product(p) for p in all_products]


def search(query):
    logger.info("vitrine busca: {q}", q=query)

    q = query.lower().strip()
    all_products = products.find(is_active=True)
    result = []
    for p in all_products:
        p = deserialize(p)
        name = p.get("name", "").lower()
        desc = p.get("description", "").lower()
        if q in name or q in desc:
            result.append(_enrich_product(p))
    return result


def list_by_merchant(merchant_id):
    logger.info("vitrine por merchant: {mid}", mid=merchant_id)

    all_products = products.find(merchant_id=merchant_id, is_active=True)
    return [_enrich_product(p) for p in all_products]


def list_open_merchants():
    logger.info("vitrine: merchants abertos")

    open_merchants = merchants.find(is_open=True, status=True)
    result = []
    for m in open_merchants:
        m = deserialize(m)
        result.append({
            "id": str(m["id"]),
            "name": m.get("name", ""),
            "logo_url": m.get("logo_url", ""),
            "is_open": m.get("is_open", False),
            "taxa_delivery": float(m.get("taxa_delivery", 0)),
            "categories": m.get("categories", []),
            "rating": float(m.get("rating", 0)),
            "opening_hours": m.get("opening_hours", ""),
            "delivery_time": int(m.get("delivery_time", 30)),
            "address": m.get("address", ""),
        })
    return result


def get_product(product_id):
    logger.info("vitrine: produto {pid}", pid=product_id)

    p = products.get(product_id)
    if not p:
        raise NotFoundError("Produto não encontrado")

    return _enrich_product(p)


def list_categories():
    logger.info("vitrine: listar categorias")

    all_merchants = merchants.find(status=True)
    categories = set()
    for m in all_merchants:
        m = deserialize(m)
        for cat in m.get("categories", []):
            if cat:
                categories.add(cat)

    # Também busca categorias dos produtos ativos
    all_products = products.find(is_active=True)
    for p in all_products:
        p = deserialize(p)
        cat = p.get("categoria", "")
        if cat:
            categories.add(cat)

    return sorted(categories)
