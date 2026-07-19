# Database connection - esqueleto
from loguru import logger
from src.infra.config import settings
from portunus import Client

db = Client(settings.DATABASE_HOST, user=settings.DATABASE_USER, password=settings.DATABASE_PASSWORD)
DB_NAME = settings.DATABASE_NAME

clients = db.use(DB_NAME, "clients")
merchants = db.use(DB_NAME, "merchants")
drivers = db.use(DB_NAME, "drivers")
tokens = db.use(DB_NAME, "tokens")
products = db.use(DB_NAME, "products")
carts = db.use(DB_NAME, "carts")
sub_ordens = db.use(DB_NAME, "sub_ordens")
ordens = db.use(DB_NAME, "ordens")
transferencias = db.use(DB_NAME, "transferencias")
recargas = db.use(DB_NAME, "recargas")
comprovantes = db.use(DB_NAME, "comprovantes")
email_confirmations = db.use(DB_NAME, "email_confirmations")
driver_history = db.use(DB_NAME, "driver_history")
coupons = db.use(DB_NAME, "coupons")
ratings = db.use(DB_NAME, "ratings")
favorites = db.use(DB_NAME, "favorites")

logger.info("banco de dados conectado: {db}", db=DB_NAME)
