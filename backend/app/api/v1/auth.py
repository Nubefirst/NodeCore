from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.auth import Token
from backend.app.dependencies.database import get_db
from backend.app.repositories.user import UserRepository
from backend.app.services.auth import AuthService

router = APIRouter()

@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and return JWT token",
    description="""
Authenticate an existing user using username and password.

Returns a JWT access token that should be included in the `Authorization` header
using the Bearer scheme.
""",
    responses={
    status.HTTP_200_OK: {
        "description": "JWT access token returned successfully.",
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Invalid username or password.",
    },
}
)
async def user_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):

        repository = UserRepository(db)
        service = AuthService(repository)

        access_token = await service.login(
                form_data.username,
                form_data.password
        )

        if access_token is None:
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                )

        return {
                "access_token": access_token,
                "token_type": "bearer"
        }