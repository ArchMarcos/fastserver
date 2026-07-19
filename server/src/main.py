# FastAPI entry point
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from src.infra.config import settings
from src.infra.errors import AppError
from src.routes.auth import router as auth_router
from src.routes.merchants import router as merchants_router
from src.routes.clients import router as clients_router
from src.routes.ordem import router as ordem_router
from src.routes.drivers import router as drivers_router
from src.routes.notifications import router as notif_router


def create_app() -> FastAPI:
    logger.info("criando app FastAPI")

    app = FastAPI(
        title=settings.PLATFORM_NAME,
        version="0.1.0",
        description="API de delivery",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.warning("AppError {code}: {msg}", code=exc.status_code, msg=exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error_code": exc.error_code},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.error("Erro não tratado: {exc}", exc=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"},
        )

    # Registra rotas diretamente no create_app
    register_routes(app)

    return app


def register_routes(app: FastAPI):
    logger.info("registrando rotas")
    app.include_router(auth_router)
    app.include_router(merchants_router)
    app.include_router(clients_router)
    app.include_router(ordem_router)
    app.include_router(drivers_router)
    app.include_router(notif_router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": settings.PLATFORM_NAME}


def register_middlewares(app: FastAPI):
    logger.info("middlewares já configurados no create_app")
    pass


def run():
    logger.info(
        "iniciando servidor em {host}:{port}",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
    )
    app = create_app()
    register_routes(app)
    register_middlewares(app)

    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower() if hasattr(settings, "LOG_LEVEL") else "info",
    )


if __name__ == "__main__":
    run()
