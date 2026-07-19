# Merchant products — CRUD completo
from loguru import logger

from src.database.database import products, merchants
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError, ValidationError
from src.infra.config import settings


def new_product(merchant_id, name, description, images, acompanhamentos, price, categoria):
    logger.info("novo produto merchant: {mid} nome: {name}", mid=merchant_id, name=name)

    # Verifica se merchant existe
    merchant_data = merchants.get(merchant_id)
    if not merchant_data:
        raise NotFoundError("Merchant não encontrado")

    merchant_data = deserialize(merchant_data)

    product_data = {
        "merchant_id": str(merchant_id),
        "name": name,
        "description": description,
        "images_url": images or [],
        "acompanhamentos": acompanhamentos or {},
        "price": price,
        "categoria": categoria or "",
        "is_active": True,
        "discount": 0.0,
    }

    serialized = serialize(product_data)
    created = products.create(**serialized)

    # Deserializa para converter JSON strings de volta a list/dict
    created = deserialize(created)

    # Atualiza lista de produtos do merchant
    product_list = merchant_data.get("products", [])
    product_list.append(str(created["id"]))
    merchants.update(serialize({"products": product_list}), id=merchant_id)

    return {
        "id": str(created["id"]),
        "merchant_id": str(created["merchant_id"]),
        "name": created["name"],
        "description": created.get("description", ""),
        "images_url": created.get("images_url", []),
        "acompanhamentos": created.get("acompanhamentos", {}),
        "price": float(created["price"]),
        "categoria": created.get("categoria", ""),
        "is_active": created.get("is_active", True),
        "discount": float(created.get("discount", 0.0)),
        "created_at": str(created.get("created_at", "")),
        "updated_at": str(created.get("updated_at", "")),
    }


def update_product(product_id, field, value):
    logger.info("produto atualizado: {pid} campo: {field}", pid=product_id, field=field)

    product_data = products.get(product_id)
    if not product_data:
        raise NotFoundError("Produto não encontrado")

    allowed_fields = {"name", "description", "price", "categoria"}
    if field not in allowed_fields:
        raise ValidationError(f"Campo '{field}' não pode ser alterado")

    products.update({field: value}, id=product_id)
    return {"message": f"Produto atualizado: {field}"}


def remove_product(product_id):
    logger.info("produto removido: {pid}", pid=product_id)

    product_data = products.get(product_id)
    if not product_data:
        raise NotFoundError("Produto não encontrado")

    product_data = deserialize(product_data)
    merchant_id = product_data["merchant_id"]

    products.delete(id=product_id)

    # Remove da lista do merchant
    merchant_data = merchants.get(merchant_id)
    if merchant_data:
        merchant_data = deserialize(merchant_data)
        product_list = [p for p in merchant_data.get("products", []) if str(p) != str(product_id)]
        merchants.update(serialize({"products": product_list}), id=merchant_id)

    return {"message": "Produto removido com sucesso"}


def list_my_products(merchant_id):
    logger.info("listar produtos do merchant: {mid}", mid=merchant_id)

    all_products = products.find(merchant_id=merchant_id)
    result = []
    for p in all_products:
        p = deserialize(p)
        result.append({
            "id": str(p["id"]),
            "merchant_id": str(p["merchant_id"]),
            "name": p["name"],
            "description": p.get("description", ""),
            "images_url": p.get("images_url", []),
            "acompanhamentos": p.get("acompanhamentos", {}),
            "price": float(p["price"]),
            "categoria": p.get("categoria", ""),
            "is_active": p.get("is_active", True),
            "discount": float(p.get("discount", 0.0)),
            "created_at": str(p.get("created_at", "")),
            "updated_at": str(p.get("updated_at", "")),
        })
    return result


def toggle_active(product_id):
    logger.info("ativar/desativar produto: {pid}", pid=product_id)

    product_data = products.get(product_id)
    if not product_data:
        raise NotFoundError("Produto não encontrado")

    product_data = deserialize(product_data)
    new_status = not product_data.get("is_active", True)
    products.update({"is_active": new_status}, id=product_id)

    status = "ativado" if new_status else "desativado"
    return {"message": f"Produto {status}", "is_active": new_status}


def apply_discount(product_id, discount):
    logger.info("desconto aplicado: {pid} valor: {disc}", pid=product_id, disc=discount)

    product_data = products.get(product_id)
    if not product_data:
        raise NotFoundError("Produto não encontrado")

    if discount < 0 or discount > 100:
        raise ValidationError("Desconto deve ser entre 0 e 100")

    products.update({"discount": discount}, id=product_id)
    return {"message": f"Desconto de {discount}% aplicado", "discount": discount}
