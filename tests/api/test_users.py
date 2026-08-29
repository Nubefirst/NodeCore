from fastapi.testclient import TestClient
from datetime import datetime, timezone

from backend.app.main import app
from backend.app.models.user import User
from backend.app.security.dependencies import get_current_user


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