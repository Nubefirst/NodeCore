from backend.app.repositories.user import UserRepository
from backend.app.security.password import verify_password
from backend.app.security.jwt import create_access_token

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

        return access_token





