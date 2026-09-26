from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import db
from backend.app.core.enums import UserRole
from backend.app.dependencies.database import get_db
from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.schemas.user import UserCreate, UserRead, UserMeUpdate, UserAdminUpdate
from backend.app.security.dependencies import (
    get_current_active_user,
    get_current_user,
    require_admin,
)
from backend.app.security.password import hash_password
from backend.app.services.user import UserService

router = APIRouter(tags=["users"])


@router.post("/", response_model=UserRead)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=UserRole.USER,
        is_active=True,
    )

    user = await repository.create(user)

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
    return  await service.get_all()


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

@router.patch("/me", response_model=UserRead)
async def user_update(
        data: UserMeUpdate,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
):

    repository = UserRepository(db)
    service = UserService(repository)

    user = await service.update(current_user,data)

    await db.commit()

    return user


@router.patch("/{user_id}", response_model=UserRead)
async def user_update(
        user_id: int,
        data: UserAdminUpdate,
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = UserService(repository)
    user = await service.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await service.deactivate(user)
    await db.commit()
    return user



