from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.schemas.user import UserCreate, UserMeUpdate, UserAdminUpdate
from backend.app.security.password import hash_password
from backend.app.core.enums import UserRole
from backend.app.core.exceptions import ConflictError

from sqlalchemy.exc import IntegrityError


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_by_username(self, username: str) -> User | None:
        return await self.repository.get_by_username(username)


    async def get_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_by_id(user_id)


    async def get_all(self) -> list[User]:
        return await self.repository.get_all()


    async def create(self, data: UserCreate) -> User:
        existing_user = await self.repository.get_by_username(data.username)

        if existing_user:
            raise ConflictError("Username already exists")

        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            role=UserRole.USER,
            is_active=True,
        )

        try:
            return await self.repository.create(user)
        except IntegrityError as exc:
            await self.repository.session.rollback()

            constraint_name = getattr(
                getattr(exc.orig, "diag", None),
                "constraint_name",
                None,
            )

            if constraint_name == "users_username_key":
                raise ConflictError("Username already exists") from exc

            raise


    async def update(
        self,
        user: User,
        data: UserMeUpdate | UserAdminUpdate
    ) -> User:
        if data.username is not None:
            user.username = data.username

        if data.password is not None:
            user.password_hash = hash_password(data.password)

        if isinstance(data, UserAdminUpdate):
            if data.role is not None:
                user.role = data.role

            if data.is_active is not None:
                user.is_active = data.is_active

        await self.repository.session.flush()
        await self.repository.session.refresh(user)

        return user


    async def deactivate(self, user: User) -> None:
        await self.repository.deactivate(user)