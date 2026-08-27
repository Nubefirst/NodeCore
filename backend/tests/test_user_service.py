import asyncio
import uuid

from backend.app.db.session import async_session_factory
from backend.app.repositories.user import UserRepository
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.security.password import verify_password
from backend.app.services.user import UserService


async def main():
    async with async_session_factory() as session:
        repo = UserRepository(session)
        service = UserService(repo)

        # Делаем username уникальным, чтобы тест можно было запускать много раз
        username = f"test_{uuid.uuid4().hex[:8]}"

        # --------------------------------------------------
        # 1. CREATE
        # --------------------------------------------------
        print("1. Создаём пользователя...")

        user = await service.create(
            UserCreate(
                username=username,
                password="12345678",
                role="admin",
            )
        )
        await session.commit()

        assert user.id is not None
        assert user.username == username
        assert user.role == "admin"
        assert user.is_active is True

        print("✅ Создание пользователя — OK")

        # --------------------------------------------------
        # 2. PASSWORD HASH
        # --------------------------------------------------
        print("\n2. Проверяем хеширование пароля...")

        assert user.password_hash != "12345678"
        assert user.password_hash.startswith("$argon2")
        assert verify_password("12345678", user.password_hash)
        assert not verify_password("wrong_password", user.password_hash)

        print("✅ Пароль захеширован — OK")

        # --------------------------------------------------
        # 3. GET BY USERNAME
        # --------------------------------------------------
        print("\n3. Получаем пользователя по username...")

        found_user = await service.get_by_username(username)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == username

        print("✅ Получение пользователя — OK")

        # --------------------------------------------------
        # 4. DUPLICATE USERNAME
        # --------------------------------------------------
        print("\n4. Проверяем дубликат username...")

        try:
            await service.create(
                UserCreate(
                    username=username,
                    password="87654321",
                    role="user",
                )
            )
            raise AssertionError("Дубликат username был создан.")
        except ValueError as e:
            assert str(e) == "Username already exists"

        print("✅ Дубликат username отклонён — OK")

        # --------------------------------------------------
        # 5. UPDATE USER
        # --------------------------------------------------
        print("\n5. Обновляем пользователя...")

        updated_user = await service.update(
            found_user,
            UserUpdate(
                username=f"{username}_updated",
                role="user",
                password="new_password",
            ),
        )
        await session.commit()

        assert updated_user.username == f"{username}_updated"
        assert updated_user.role == "user"

        # Новый пароль тоже должен быть захеширован
        assert updated_user.password_hash != "new_password"
        assert verify_password("new_password", updated_user.password_hash)
        assert not verify_password("12345678", updated_user.password_hash)

        print("✅ Обновление пользователя — OK")

        # --------------------------------------------------
        # 6. GET UPDATED USER
        # --------------------------------------------------
        print("\n6. Проверяем обновлённого пользователя...")

        found_updated = await service.get_by_username(f"{username}_updated")

        assert found_updated is not None
        assert found_updated.id == user.id
        assert found_updated.username == f"{username}_updated"

        print("✅ Обновлённый пользователь найден — OK")

        # --------------------------------------------------
        # 7. DEACTIVATE USER
        # --------------------------------------------------
        print("\n7. Деактивируем пользователя...")

        await service.deactivate(found_updated)
        await session.commit()

        deactivated_user = await service.get_by_username(f"{username}_updated")

        assert deactivated_user is not None
        assert deactivated_user.is_active is False

        print("✅ Деактивация пользователя — OK")

        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------
        print("\n🎉 Все тесты UserService успешно пройдены!")


if __name__ == "__main__":
    asyncio.run(main())