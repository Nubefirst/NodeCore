from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from backend.app.core.enums import UserRole
from backend.app.models.user import User
from backend.app.security.dependencies import get_current_user
from backend.app.main import app
from backend.app.dependencies.database import get_db
from backend.app.security.password import verify_password








def test_get_current_user():
    fake_user = User(
        id=123,
        username="testuser",
        password_hash="secret_hash",
        is_active=True,
        role="user",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def override_get_current_user():
        return fake_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        client = TestClient(app)
        response = client.get("/users/me")

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == 123
        assert data["username"] == "testuser"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "password_hash" not in data

    finally:
        app.dependency_overrides.clear()


def test_create_user_password_hashed():
    user_data = {
        "username": "testuser",
        "password": "secret123",
    }

    fake_user = MagicMock()
    fake_user.username = user_data["username"]
    fake_user.password_hash = "hashed_secret123"
    fake_user.role = UserRole.USER
    fake_user.is_active = True

    mock_repository = MagicMock()
    mock_repository.create = AsyncMock(return_value=fake_user)

    async def override_get_db():
        db = MagicMock()
        db.commit = AsyncMock()
        return db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                "backend.app.api.v1.users.UserRepository",
                lambda db: mock_repository,
            )

            client = TestClient(app)
            response = client.post("/users/", json=user_data)

            assert response.status_code == 200
            data = response.json()
            assert data["username"] == user_data["username"]
            assert "password_hash" not in data

            call_args = mock_repository.create.call_args[0][0]
            assert call_args.username == user_data["username"]
            assert call_args.password_hash != user_data["password"]
            assert verify_password(user_data["password"], call_args.password_hash) is True
            assert call_args.role == UserRole.USER
            assert call_args.is_active is True

    finally:
        app.dependency_overrides.clear()