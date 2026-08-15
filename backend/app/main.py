from fastapi import FastAPI

from backend.app.api.v1.health import router as health_router
from backend.app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(
    health_router,
    prefix="/api/v1/health",
    tags=["Health"],
)