import asyncio
import selectors

from backend.app.db.session import async_session_factory
from backend.app.repositories.user import UserRepository
from backend.app.models.user import User
from backend.app.core.enums import UserRole
from backend.app.security.password import hash_password


async def main():
    async with async_session_factory() as session:

        repository = UserRepository(session)

        existing = await repository.get_by_username("admin")
        if existing is not None:
            print("Admin already exists")
            return

        password = "12345678"
        user = User(
            username="admin",
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )

        await repository.create(user)
        await session.commit()

        print("Admin created successfully")


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )