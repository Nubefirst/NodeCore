from fastapi import FastAPI

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.users import router as users_router
from backend.app.core.config import settings


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