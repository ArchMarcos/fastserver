# ---------------
# conexão PortunusQL — um Client por tabela
# ---------------
import json
from portunus import Client
from loguru import logger
from src.infra.config import settings

DB = settings.DATABASE_NAME

# -- campos que PortunusQL não aceita nativamente (list/dict) --
_SERIALIZE_FIELDS: set[str] = {
    "cart", "ordem", "favorites", "addresses", "products", "ordens",
    "categories", "ordens_disponiveis", "images_url", "notify",
    "merchant_ids", "sub_ordens", "pegar_em", "acompanhamentos",
}


def serialize(data: dict) -> dict:
    """Converte list/dict para string JSON antes de gravar no banco."""
    return {
        k: json.dumps(v) if k in _SERIALIZE_FIELDS and isinstance(v, (list, dict)) else v
        for k, v in data.items()
    }


def deserialize(data: dict) -> dict:
    """Converte string JSON de volta para list/dict ao ler do banco."""
    return {
        k: json.loads(v) if k in _SERIALIZE_FIELDS and isinstance(v, str) else v
        for k, v in data.items()
    }


# Autentica uma vez e reusa o token em todos os clients
# (cada login separado sobrescreveria o token do usuário no servidor)
_AUTH_TOKEN: str | None = None


def _get_token() -> str:
    """Obtém um token de autenticação (uma única vez)."""
    global _AUTH_TOKEN
    if _AUTH_TOKEN is None:
        temp = Client(
            settings.DATABASE_HOST,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
        )
        _AUTH_TOKEN = temp._token
    return _AUTH_TOKEN


def _make_client(table: str) -> Client:
    """Cria um Client isolado para a tabela — reusa o token global."""
    return Client(
        settings.DATABASE_HOST,
        user=settings.DATABASE_USER,
        token=_get_token(),
        database=DB,
        table=table,
    )


# -- 16 tabelas, cada uma com seu próprio Client --
clients = _make_client("clients")
merchants = _make_client("merchants")
drivers = _make_client("drivers")
tokens = _make_client("tokens")
products = _make_client("products")
carts = _make_client("carts")
sub_ordens = _make_client("sub_ordens")
ordens = _make_client("ordens")
transferencias = _make_client("transferencias")
recargas = _make_client("recargas")
comprovantes = _make_client("comprovantes")
email_confirmations = _make_client("email_confirmations")
driver_history = _make_client("driver_history")
coupons = _make_client("coupons")
ratings = _make_client("ratings")
favorites = _make_client("favorites")

logger.info("banco conectado — {db} ({n} tabelas)", db=DB, n=16)
