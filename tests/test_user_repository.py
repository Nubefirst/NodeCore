from backend.app.repositories.user import UserRepository
from backend.app.db.session import async_session_factory
from backend.app.models.user import User

async def main():
    async with async_session_factory() as session:

        repository = UserRepository(session)

        user = User(
            username="repository_test",
            password_hash="test",
            role="user",
            is_active=True,
        )

        created_user = await repository.create(user)

        await session.commit()

        print(created_user.id)
        print(created_user.username)

        found_user = await repository.get_by_username(
            "repository_test"
        )

        print(found_user)