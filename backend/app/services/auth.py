from backend.app.repositories.user import UserRepository
from backend.app.security.password import verify_password
from backend.app.security.jwt import create_access_token, create_refresh_token, decode_refresh_token


class AuthService:

    def __init__(self, repository: UserRepository):
        self.repository = repository


    async def login(self, username, password):
        user = await self.repository.get_by_username(username)

        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }


    async def refresh(self, refresh_token):
        payload = decode_refresh_token(refresh_token)

        sub = payload.get("sub")
        if sub is None:
            return None

        try:
            user_id = int(sub)
        except (ValueError, TypeError):
            return None

        user = await self.repository.get_by_id(user_id)
        if user is None:
            return None

        if not user.is_active:
            return None

        access_token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
        }




