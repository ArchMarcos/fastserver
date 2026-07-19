# Custom exceptions - with HTTP status codes


class AppError(Exception):
    """Erro genérico da aplicação."""
    status_code = 500

    def __init__(self, message: str = "Erro interno", error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthError(AppError):
    """Erro de autenticação."""
    status_code = 401


class NotFoundError(AppError):
    """Recurso não encontrado."""
    status_code = 404


class PaymentError(AppError):
    """Erro de pagamento."""
    status_code = 402


class ValidationError(AppError):
    """Erro de validação."""
    status_code = 422
