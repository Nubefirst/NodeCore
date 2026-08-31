import jwt

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.security.jwt import decode_access_token
from backend.app.security.oauth2 import oauth2_scheme
from backend.app.dependencies.database import get_db
from backend.app.repositories.user import UserRepository

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
     try:
          payload = decode_access_token(token)
     except jwt.ExpiredSignatureError:
          raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Token expired",
               headers={"WWW-Authenticate": "Bearer"},
          ) from None
     except jwt.InvalidTokenError:
          raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid token",
               headers={"WWW-Authenticate": "Bearer"},
          ) from None

     sub = payload.get("sub")

     if sub is None:
          raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid token payload: missing 'sub'",
               headers={"WWW-Authenticate": "Bearer"},
          )

     try:
          user_id = int(sub)
     except (ValueError, TypeError):
          raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid token payload: 'sub' must be a valid integer",
               headers={"WWW-Authenticate": "Bearer"},
          ) from None


     repository = UserRepository(db)
     user = await repository.get_by_id(user_id)

     if user is None:
          raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="User not found",
               headers={"WWW-Authenticate": "Bearer"},
          )

     return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
     if not current_user.is_active:
          raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Inactive user",
          )
     return current_user




