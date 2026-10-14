from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.users import router as users_router
from backend.app.core.config import settings
from backend.app.core.exceptions import AppError
from backend.app.core.logger import logger
from backend.app.middlewares.request_logging import RequestLoggingMiddleware

openapi_tags = [
    {
        "name": "Authentication",
        "description": "Login and JWT authentication endpoints.",
    },
    {
        "name": "Users",
        "description": "Operations for creating and retrieving users.",
    },
    {
        "name": "Health",
        "description": "Application and database health checks.",
    },
]


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
NodeCore API — backend для управления Linux-серверами.

Включает:

- аутентификацию пользователей;
- управление пользователями;
- проверку состояния приложения и базы данных.
""",
    contact={"name": "NodeCore Team"},
    license_info={"name": "MIT"},
    openapi_tags=openapi_tags,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    exc: AppError,
):
    logger.warning(
        "Application error: {} {} | {} | {}",
        request.method,
        request.url.path,
        exc.code,
        exc.message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


@app.exception_handler(Exception)
async def internal_error_handler(
    request: Request,
    exc: Exception,
):
    logger.opt(exception=exc).error(
        "Unhandled exception: {} {}",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Internal server error",
            }
        },
    )


app.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    health_router,
    prefix="/api/v1/health",
    tags=["Health"],
)
