from fastapi import APIRouter

from backend.app.schemas.system import SystemInfoResponse
from backend.app.services.system import SystemService

router = APIRouter()


@router.get(
    "/info",
    response_model=SystemInfoResponse,
)
def get_system_info():
    return SystemService.get_system_info()
