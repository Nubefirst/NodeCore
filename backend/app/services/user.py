from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_by_username(self, username: str) -> User | None:
        return await self.repository.get_by_username(username)

    async def create(self, data: UserCreate) -> User:
        # Проверяем, что пользователь с таким username не существует
        existing_user = await self.repository.get_by_username(data.username)
        if existing_user:
            raise ValueError("Username already exists")

        # Пока сохраняем пароль как есть.
        # Позже здесь будет хеширование.
        user = User(
            username=data.username,
            password=data.password,
            role=data.role,
            is_active=data.is_active,
        )

        return await self.repository.create(user)

    async def update(self, user: User, data: UserUpdate) -> User:
        if data.username is not None:
            user.username = data.username

        if data.role is not None:
            user.role = data.role

        if data.is_active is not None:
            user.is_active = data.is_active

        if data.password is not None:
            # Позже здесь тоже будет хеширование.
            user.password = data.password

        await self.repository.session.flush()
        await self.repository.session.refresh(user)

        return user

    async def deactivate(self, user: User) -> None:
        await self.repository.deactivate(user)