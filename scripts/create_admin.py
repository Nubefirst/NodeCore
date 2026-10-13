import asyncio
import selectors
import os
import getpass

from backend.app.db.session import async_session_factory
from backend.app.repositories.user import UserRepository
from backend.app.models.user import User
from backend.app.core.enums import UserRole
from backend.app.security.password import hash_password

def get_admin_password() -> str:
    password = os.getenv("NODECORE_ADMIN_PASSWORD")

    if password == "":
        raise ValueError("NODECORE_ADMIN_PASSWORD is set but empty")

    if password is None:
        password = getpass.getpass("Enter admin password: ")


    if not password.strip():
        raise ValueError("Password cannot be empty or whitespace")

    return password


async def main():
    async with async_session_factory() as session:

        repository = UserRepository(session)

        existing = await repository.get_by_username("admin")
        if existing is not None:
            print("Admin already exists")
            return

        password = get_admin_password()
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