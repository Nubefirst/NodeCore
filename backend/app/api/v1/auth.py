from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.auth import Token
from backend.app.dependencies.database import get_db
from backend.app.repositories.user import UserRepository
from backend.app.security.jwt import create_access_token
from backend.app.security.password import verify_password, hash_password

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=Token)
async def user_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):

        repository = UserRepository(db)
        user = await repository.get_by_username(form_data.username)
        if user is None:
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"}
                )

        if not verify_password(form_data.password, user.password_hash):
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                )

        access_token = create_access_token({"sub": str(user.id)})

        return {
                "access_token": access_token,
                "token_type": "bearer"
        }