# Cart do cliente — carrinho armazenado no documento do cliente
from loguru import logger

from src.database.database import clients, products, merchants
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, ValidationError
from src.infra.config import settings


def _get_cart_data(client_id):
    """Busca cliente e retorna (client_data, cart)."""
    client_data = clients.get(client_id)
    if not client_data:
        raise NotFoundError("Cliente não encontrado")
    client_data = deserialize(client_data)
    cart = client_data.get("cart", [])
    return client_data, cart


def _save_cart(client_id, cart):
    """Serializa e salva o carrinho no documento do cliente."""
    serialized = serialize({"cart": cart})
    clients.update(serialized, id=client_id)


def _build_item(product_id, merchant_id, quantidade, acompanhamentos, obs):
    """Busca produto e monta item do carrinho."""
    p = products.get(product_id)
    if not p:
        raise NotFoundError("Produto não encontrado")
    p = deserialize(p)

    if not p.get("is_active", True):
        raise ValidationError("Produto não está disponível")

    price = float(p["price"])
    discount = float(p.get("discount", 0))
    unit_price = price * (1 - discount / 100) if discount > 0 else price

    return {
        "product_id": str(p["id"]),
        "merchant_id": merchant_id,
        "product_name": p["name"],
        "price": unit_price,
        "quantidade": quantidade,
        "acompanhamentos": acompanhamentos or {},
        "obs": obs or "",
        "total": round(unit_price * quantidade, 2),
    }


def add_to_cart(client_id, product_id, merchant_id, quantidade=1, acompanhamentos=None, obs=""):
    logger.info("add carrinho: {cid} produto: {pid}", cid=client_id, pid=product_id)

    client_data, cart = _get_cart_data(client_id)

    # Se carrinho vazio, aceita qualquer merchant; se já tem itens, verifica mesmo merchant
    if cart:
        existing_merchant = cart[0].get("merchant_id")
        if existing_merchant != merchant_id:
            raise ValidationError("Carrinho já contém itens de outro merchant. Finalize o pedido ou limpe o carrinho.")

    # Verifica se produto já está no carrinho (atualiza quantidade)
    for item in cart:
        if item.get("product_id") == product_id:
            item["quantidade"] += quantidade
            item["total"] = round(item["price"] * item["quantidade"], 2)
            _save_cart(client_id, cart)
            return _calc_response(cart)

    # Novo item
    item = _build_item(product_id, merchant_id, quantidade, acompanhamentos, obs)
    cart.append(item)
    _save_cart(client_id, cart)

    return _calc_response(cart)


def remove_from_cart(client_id, product_id):
    logger.info("remove carrinho: {cid} produto: {pid}", cid=client_id, pid=product_id)

    _, cart = _get_cart_data(client_id)
    cart = [i for i in cart if i.get("product_id") != product_id]
    _save_cart(client_id, cart)
    return _calc_response(cart)


def update_quantity(client_id, product_id, quantidade):
    logger.info("qtd carrinho: {cid} produto: {pid} qtd: {q}", cid=client_id, pid=product_id, q=quantidade)

    _, cart = _get_cart_data(client_id)
    for item in cart:
        if item.get("product_id") == product_id:
            item["quantidade"] = quantidade
            item["total"] = round(item["price"] * quantidade, 2)
            _save_cart(client_id, cart)
            return _calc_response(cart)

    raise NotFoundError("Produto não encontrado no carrinho")


def update_obs(client_id, product_id, obs):
    logger.info("obs carrinho: {cid} produto: {pid}", cid=client_id, pid=product_id)

    _, cart = _get_cart_data(client_id)
    for item in cart:
        if item.get("product_id") == product_id:
            item["obs"] = obs
            _save_cart(client_id, cart)
            return _calc_response(cart)

    raise NotFoundError("Produto não encontrado no carrinho")


def get_cart(client_id):
    logger.info("get carrinho: {cid}", cid=client_id)

    _, cart = _get_cart_data(client_id)
    return _calc_response(cart)


def clear_cart(client_id):
    logger.info("limpar carrinho: {cid}", cid=client_id)

    _save_cart(client_id, [])
    return _calc_response([])


def calc_cart_totals(client_id):
    logger.info("totais carrinho: {cid}", cid=client_id)

    _, cart = _get_cart_data(client_id)
    return _calc_response(cart)


def _calc_response(cart):
    """Monta resposta padronizada do carrinho."""
    if not cart:
        return {
            "merchant_id": "",
            "merchant_name": "",
            "items": [],
            "total_products": 0.0,
            "total_delivery_fee": 0.0,
            "total_platform_tax": 0.0,
            "total": 0.0,
        }

    merchant_id = cart[0].get("merchant_id", "")
    merchant_name = ""
    if merchant_id:
        m = merchants.get(merchant_id)
        if m:
            m = deserialize(m)
            merchant_name = m.get("name", "")

    total_products = round(sum(i.get("total", 0) for i in cart), 2)
    platform_tax = round(total_products * settings.PLATFORM_TAX, 2)

    delivery_fee = 0.0
    if merchant_id:
        m = merchants.get(merchant_id)
        if m:
            m = deserialize(m)
            delivery_fee = float(m.get("taxa_delivery", 0))

    total = round(total_products + delivery_fee + platform_tax, 2)

    return {
        "merchant_id": merchant_id,
        "merchant_name": merchant_name,
        "items": [
            {
                "product_id": i.get("product_id", ""),
                "merchant_id": i.get("merchant_id", ""),
                "product_name": i.get("product_name", ""),
                "price": float(i.get("price", 0)),
                "quantidade": int(i.get("quantidade", 1)),
                "acompanhamentos": i.get("acompanhamentos", {}),
                "obs": i.get("obs", ""),
                "total": float(i.get("total", 0)),
            }
            for i in cart
        ],
        "total_products": total_products,
        "total_delivery_fee": delivery_fee,
        "total_platform_tax": platform_tax,
        "total": total,
    }
