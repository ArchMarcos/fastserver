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


def _create_token() -> str:
    """Faz login no Portunus e retorna um token novo."""
    temp = Client(
        settings.DATABASE_HOST,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
    )
    return temp._token


def _get_token() -> str:
    """Obtém um token de autenticação (com cache)."""
    global _AUTH_TOKEN
    if _AUTH_TOKEN is None:
        _AUTH_TOKEN = _create_token()
    return _AUTH_TOKEN


def refresh_token():
    """Força um novo login no Portunus (use após reiniciar o banco)."""
    global _AUTH_TOKEN
    _AUTH_TOKEN = _create_token()
    logger.info("token Portunus renovado")


class _PortunusClient(Client):
    """Wrapper que reautentica automaticamente se o token expirar."""

    def _execute(self, query: str):
        try:
            return super()._execute(query)
        except Exception as e:
            if "invalid or expired token" in str(e).lower() or "authentication failed" in str(e).lower():
                refresh_token()
                self._token = _AUTH_TOKEN
                return super()._execute(query)
            raise


def _make_client(table: str) -> Client:
    """Cria um Client isolado para a tabela — reusa o token global."""
    return _PortunusClient(
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
