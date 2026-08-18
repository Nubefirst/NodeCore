from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.user import User

class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_username(
        self,
        username: str
    ) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def create(
            self,
            user: User,
    ) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user


    async def deactivate(self, user: User) -> None:
        user.is_active = False
        await self.session.flush()
