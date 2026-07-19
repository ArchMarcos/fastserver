# Notificações in-app — persistidas no campo `notify` do usuário
from loguru import logger

from src.database.database import clients, merchants, drivers
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError

MAX_NOTIFY = 10

_COLLECTIONS = {"client": clients, "merchant": merchants, "driver": drivers}


def send(user_id, role, title, body, tipo="info"):
    """Envia notificação in-app persistindo no documento do usuário."""
    col = _COLLECTIONS.get(role)
    if not col:
        return None

    user = col.get(user_id)
    if not user:
        return None

    user = deserialize(user)
    notifications = user.get("notify", [])
    notification = {"title": title, "body": body, "tipo": tipo, "read": False}
    notifications.insert(0, notification)

    if len(notifications) > MAX_NOTIFY:
        notifications = notifications[:MAX_NOTIFY]

    col.update(serialize({"notify": notifications}), id=user_id)
    logger.info("notificação in-app: {uid} ({role}): {title}", uid=user_id, role=role, title=title)
    return notification


def list_by_user(user_id, role):
    """Lista notificações do usuário."""
    col = _COLLECTIONS.get(role)
    if not col:
        return []

    user = col.get(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    return deserialize(user).get("notify", [])


def clear(user_id, role):
    """Limpa todas as notificações do usuário."""
    col = _COLLECTIONS.get(role)
    if not col:
        return {"message": "Nenhuma ação necessária"}

    if not col.get(user_id):
        raise NotFoundError("Usuário não encontrado")

    col.update(serialize({"notify": []}), id=user_id)
    return {"message": "Notificações limpas com sucesso"}
