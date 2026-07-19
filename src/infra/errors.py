# Custom exceptions - esqueleto


class AppError(Exception):
    """Erro genérico da aplicação."""


class AuthError(AppError):
    """Erro de autenticação."""


class NotFoundError(AppError):
    """Recurso não encontrado."""


class PaymentError(AppError):
    """Erro de pagamento."""


class ValidationError(AppError):
    """Erro de validação."""
