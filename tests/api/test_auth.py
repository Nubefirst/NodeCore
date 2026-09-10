import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from backend.app.main import app
from backend.app.dependencies.database import get_db
from backend.app.repositories.user import UserRepository
from backend.app.security.password import hash_password


@pytest.fixture
def client():
    """Фикстура для создания тестового клиента."""
    return TestClient(app)


@pytest.mark.asyncio
def test_login_success(client):
    """1. Правильные username + password → 200 + JWT."""
    hashed_password = hash_password("secret123")
    fake_user = MagicMock()
    fake_user.id = 123
    fake_user.username = "testuser"
    fake_user.password_hash = hashed_password

    mock_repository = MagicMock()
    mock_repository.get_by_username = AsyncMock(return_value=fake_user)

    async def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                "backend.app.api.v1.auth.UserRepository",
                lambda db: mock_repository,
            )

            response = client.post(
                "/auth/login",
                data={
                    "username": "testuser",
                    "password": "secret123",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert isinstance(data["access_token"], str)
            assert len(data["access_token"]) > 0

            mock_repository.get_by_username.assert_awaited_once_with("testuser")

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
def test_login_wrong_password(client):
    """2. Правильный username, неправильный пароль → 401."""
    # 1. Подготовка: создаём пользователя с хешем
    hashed_password = hash_password("secret123")
    fake_user = MagicMock()
    fake_user.id = 123
    fake_user.username = "testuser"
    fake_user.password_hash = hashed_password

    # 2. Мокаем репозиторий
    mock_repository = MagicMock()
    mock_repository.get_by_username = AsyncMock(return_value=fake_user)

    # 3. Переопределяем зависимости
    async def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                "backend.app.api.v1.auth.UserRepository",
                lambda db: mock_repository,
            )

            # 4. Отправляем запрос с НЕПРАВИЛЬНЫМ паролем
            response = client.post(
                "/auth/login",
                data={
                    "username": "testuser",
                    "password": "wrong_password",
                },
            )

            # 5. Проверяем
            assert response.status_code == 401
            data = response.json()
            assert data["detail"] == "Invalid credentials"
            assert "access_token" not in data

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
def test_login_user_not_found(client):
    """3. Несуществующий username → 401."""
    # 1. Мокаем репозиторий (возвращает None)
    mock_repository = MagicMock()
    mock_repository.get_by_username = AsyncMock(return_value=None)

    # 2. Переопределяем зависимости
    async def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                "backend.app.api.v1.auth.UserRepository",
                lambda db: mock_repository,
            )

            # 3. Отправляем запрос
            response = client.post(
                "/auth/login",
                data={
                    "username": "unknown_user",
                    "password": "secret123",
                },
            )

            # 4. Проверяем
            assert response.status_code == 401
            data = response.json()
            assert data["detail"] == "Invalid credentials"
            assert "access_token" not in data

            # 5. Проверяем, что репозиторий вызван
            mock_repository.get_by_username.assert_awaited_once_with("unknown_user")

    finally:
        app.dependency_overrides.clear()