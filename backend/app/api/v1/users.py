from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import NotFoundError
from backend.app.dependencies.database import get_db
from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.schemas.error import ErrorResponse
from backend.app.schemas.user import (
    UserAdminUpdate,
    UserCreate,
    UserMeUpdate,
    UserRead,
)
from backend.app.security.dependencies import get_current_active_user, require_admin
from backend.app.services.user import UserService

router = APIRouter()


@router.post(
    "/",
    response_model=UserRead,
    responses={
        409: {
            "description": "Username already exists",
            "model": ErrorResponse,
        },
    },
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = UserService(repository)

    user = await service.create(user_data)
    await db.commit()

    return user


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.get("/", response_model=list[UserRead])
async def get_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = UserService(repository)
    return await service.get_all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = UserService(repository)
    user = await service.get_by_id(user_id)

    if user is None:
        raise NotFoundError("User not found")

    return user


@router.patch("/me", response_model=UserRead)
async def user_update(
    data: UserMeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = UserService(repository)

    user = await service.update(current_user, data)
    await db.commit()

    return user


@router.patch("/{user_id}", response_model=UserRead)
async def admin_update_user(
    user_id: int,
    data: UserAdminUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = UserService(repository)

    user = await service.get_by_id(user_id)

    if user is None:
        raise NotFoundError("User not found")

    user = await service.update(user, data)
    await db.commit()

    return user


@router.delete("/{user_id}", response_model=UserRead)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = UserService(repository)

    user = await service.get_by_id(user_id)

    if user is None:
        raise NotFoundError("User not found")

    await service.deactivate(user)
    await db.commit()
    return user
