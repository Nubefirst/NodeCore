from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.users import router as users_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.core.config import settings
from backend.app.core.exceptions import ConflictError


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.exception_handler(ConflictError)
async def conflict_error_handler(
    request: Request,
    exc: ConflictError,
):
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "conflict",
                "message": exc.message,
            }
        },
    )


app.include_router(
    users_router,
    prefix="/users",
    tags=["users"]
)


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    health_router,
    prefix="/api/v1/health",
    tags=["Health"],
)