from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.security.dependencies import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.schemas.user import UserCreate, UserRead
from backend.app.repositories.user import UserRepository
from backend.app.models.user import User

router = APIRouter(tags=["users"])


@router.post("/", response_model=UserRead)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    user = User(
        username=user_data.username,
        password_hash=user_data.password,
        role=user_data.role,
        is_active=user_data.is_active,
    )

    user = await repository.create(user)

    await db.commit()

    return user


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
        current_user: User = Depends(get_current_user),
):

    return current_user

