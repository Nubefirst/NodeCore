from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from jwt import ExpiredSignatureError, InvalidTokenError

from backend.app.models.user import User
from backend.app.schemas.auth import Token, RefreshTokenRequest, AccessTokenResponse
from backend.app.dependencies.database import get_db
from backend.app.repositories.user import UserRepository
from backend.app.services.auth import AuthService

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=Token)
async def user_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):

        repository = UserRepository(db)
        service = AuthService(repository)

        tokens = await service.login(
                form_data.username,
                form_data.password
        )

        if tokens is None:
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                )

        return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": "bearer"
        }


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(
        data: RefreshTokenRequest,
        db: AsyncSession = Depends(get_db),
        ):

        repository = UserRepository(db)
        service = AuthService(repository)

        try:
                result = await service.refresh(data.refresh_token)


        except ExpiredSignatureError:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from None


        except InvalidTokenError:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from None


        except ValueError:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from None


        if result is None:
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail = "Invalid refresh token",
                        headers={"WWW-Authenticate": "Bearer"}
                ) from None


        return {
                "access_token": result["access_token"],
                "token_type": "bearer",
        }





