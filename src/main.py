# FastAPI entry point - esqueleto
from loguru import logger
from src.infra.config import settings


def create_app():
    logger.info("criando app")
    return None


def register_routes(app):
    logger.info("registrando rotas")
    pass


def register_middlewares(app):
    logger.info("registrando middlewares")
    pass


def run():
    logger.info("iniciando servidor em {host}:{port}", host=settings.SERVER_HOST, port=settings.SERVER_PORT)
    app = create_app()
    register_routes(app)
    register_middlewares(app)
    return app


if __name__ == "__main__":
    run()
