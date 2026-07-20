# Config centralizada - esqueleto
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_NAME = os.getenv("DATABASE_NAME")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "60"))
    JWT_EMAIL_EXPIRE_MINUTES = int(os.getenv("JWT_EMAIL_EXPIRE_MINUTES", "60"))

    # Server
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "3100"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

    # Email
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "")

    # Frontend
    APP_URL = os.getenv("APP_URL", f"http://localhost:{os.getenv('SERVER_PORT', '3101')}")

    # Platform
    PLATFORM_TAX = float(os.getenv("PLATFORM_TAX", "0.05"))
    PLATFORM_NAME = os.getenv("PLATFORM_NAME", "FastDelivery")


settings = Settings()
