class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class ConflictError(AppError):
    def __init__(
        self,
        message: str = "Username already exists",
    ):
        super().__init__(
            message,
            "conflict",
            409,
        )


class NotFoundError(AppError):
    def __init__(
        self,
        message: str = "Resource not found",
    ):
        super().__init__(
            message,
            "not_found",
            404,
        )


class UnauthorizedError(AppError):
    def __init__(
        self,
        message: str = "Unauthorized",
    ):
        super().__init__(
            message,
            "unauthorized",
            401,
        )


class ForbiddenError(AppError):
    def __init__(
        self,
        message: str = "Forbidden",
    ):
        super().__init__(
            message,
            "forbidden",
            403,
        )
