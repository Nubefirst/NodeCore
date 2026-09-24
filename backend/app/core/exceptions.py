class AppError(Exception):
    """Базовая ошибка приложения."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ConflictError(AppError):
    """Ошибка конфликта данных."""

    def __init__(self, message: str):
        super().__init__(message)