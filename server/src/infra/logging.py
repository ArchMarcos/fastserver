# Logging config - esqueleto
import sys
from loguru import logger
from src.infra.config import settings

logger.remove()

LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"  # noqa: E501

logger.add(sys.stderr, format=LOG_FORMAT, level=settings.LOG_LEVEL)

if settings.LOG_FILE:
    logger.add(settings.LOG_FILE, format=LOG_FORMAT, level=settings.LOG_LEVEL, rotation="10 MB", retention="7 days")
