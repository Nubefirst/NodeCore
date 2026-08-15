from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies.database import get_db


router = APIRouter()


@router.get("/db")
async def health_check_db(
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(text("SELECT 1"))

    return {
        "database": result.scalar() == 1,
    }