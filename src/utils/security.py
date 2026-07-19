# Security utilities - criptografia de senhas
import bcrypt
from loguru import logger


def encrypt(txt: str) -> str:
    logger.info("criptografando senha")
    return bcrypt.hashpw(txt.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify(txt: str, hash_password: str) -> bool:
    result = bcrypt.checkpw(txt.encode("utf-8"), hash_password.encode("utf-8"))
    if not result:
        logger.warning("senha inválida")
    return result
