from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from backend.app.core.enums import UserRole
from backend.app.models.user import User
from backend.app.security.dependencies import get_current_user
from backend.app.main import app
from backend.app.dependencies.database import get_db
from backend.app.security.password import verify_password


def create_fake_user(
        user_id: int = 1,
        username: str = "testuser",
        password: str = "secret123",
        role: UserRole = UserRole.USER,
        is_active: bool = True,
) -> User:
    """Создаёт фейкового пользователя для тестов."""
    from backend.app.security.password import hash_password

    user = User(
        id=user_id,
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return user


def setup_mock_repository(
    monkeypatch,
    user: User = None,
    users_list: list = None,
):
    """Настраивает мок-репозиторий."""
    mock_repository = MagicMock()
    mock_repository.get_by_id = AsyncMock(return_value=user)
    mock_repository.get_by_username = AsyncMock(return_value=user)
    mock_repository.get_all = AsyncMock(return_value=users_list or [])
    mock_repository.create = AsyncMock(return_value=user)

    # ✅ Реальная логика деактивации
    async def deactivate_side_effect(u: User) -> None:
        u.is_active = False

    mock_repository.deactivate = AsyncMock(side_effect=deactivate_side_effect)

    mock_repository.session = MagicMock()
    mock_repository.session.flush = AsyncMock()
    mock_repository.session.refresh = AsyncMock()

    monkeypatch.setattr(
        "backend.app.api.v1.users.UserRepository",
        lambda db: mock_repository,
    )
    return mock_repository


def setup_mock_db():
    """Переопределяет get_db для тестов."""

    async def override_get_db():
        db = MagicMock()
        db.commit = AsyncMock()
        return db

    app.dependency_overrides[get_db] = override_get_db


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


def test_update_current_user_username():
    """PATCH /users/me → username изменился, 200."""
    fake_user = create_fake_user(
        user_id=123,
        username="testuser",
        role=UserRole.USER,
        is_active=True,
    )

    async def override_get_current_active_user():
        return fake_user

    from backend.app.security.dependencies import get_current_active_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=fake_user)

            client = TestClient(app)
            response = client.patch(
                "/users/me",
                json={"username": "new_username"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 123
            assert data["username"] == "new_username"
            assert data["role"] == "user"
            assert data["is_active"] is True

    finally:
        app.dependency_overrides.clear()


def test_update_current_user_password():
    """PATCH /users/me → пароль изменился."""
    old_password = "old_password"
    new_password = "new_password123"

    fake_user = create_fake_user(
        user_id=123,
        username="testuser",
        password=old_password,
    )

    async def override_get_current_active_user():
        return fake_user

    from backend.app.security.dependencies import get_current_active_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=fake_user)

            client = TestClient(app)
            response = client.patch(
                "/users/me",
                json={"password": new_password},
            )

            assert response.status_code == 200

            # Старый пароль больше не подходит
            assert verify_password(old_password, fake_user.password_hash) is False
            # Новый пароль подходит
            assert verify_password(new_password, fake_user.password_hash) is True

    finally:
        app.dependency_overrides.clear()


def test_update_current_user_cannot_change_role():
    """PATCH /users/me → нельзя стать админом."""
    fake_user = create_fake_user(
        user_id=123,
        username="testuser",
        role=UserRole.USER,
    )

    async def override_get_current_active_user():
        return fake_user

    from backend.app.security.dependencies import get_current_active_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=fake_user)

            client = TestClient(app)
            response = client.patch(
                "/users/me",
                json={"username": "testuser", "role": "admin"},  # ← лишнее поле
            )

            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "user"  # ← роль не изменилась

    finally:
        app.dependency_overrides.clear()


def test_update_current_user_cannot_change_is_active():
    """PATCH /users/me → нельзя деактивировать себя."""
    fake_user = create_fake_user(
        user_id=123,
        username="testuser",
        is_active=True,
    )

    async def override_get_current_active_user():
        return fake_user

    from backend.app.security.dependencies import get_current_active_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=fake_user)

            client = TestClient(app)
            response = client.patch(
                "/users/me",
                json={"username": "testuser", "is_active": False},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["is_active"] is True  # ← не изменилось

    finally:
        app.dependency_overrides.clear()


def test_get_users_admin():
    """GET /users/ → 200 + список пользователей."""
    admin = create_fake_user(
        user_id=1,
        username="admin",
        role=UserRole.ADMIN,
    )
    users = [
        admin,
        create_fake_user(user_id=2, username="user2"),
        create_fake_user(user_id=3, username="user3"),
    ]

    async def override_require_admin():
        return admin

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, users_list=users)

            client = TestClient(app)
            response = client.get("/users/")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 3
            for user in data:
                assert "id" in user
                assert "username" in user
                assert "password_hash" not in user

    finally:
        app.dependency_overrides.clear()


def test_get_users_regular_user_forbidden():
    """GET /users/ → 403 для обычного пользователя."""
    user = create_fake_user(user_id=2, role=UserRole.USER)

    async def override_require_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin required",
        )

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        client = TestClient(app)
        response = client.get("/users/")

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()


def test_get_user_admin():
    """GET /users/123 → 200 для админа."""
    admin = create_fake_user(user_id=1, username="admin", role=UserRole.ADMIN)
    target = create_fake_user(user_id=123, username="target_user")

    async def override_require_admin():
        return admin

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=target)

            client = TestClient(app)
            response = client.get("/users/123")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 123
            assert data["username"] == "target_user"
            assert "password_hash" not in data

    finally:
        app.dependency_overrides.clear()


def test_get_user_regular_user_forbidden():
    """GET /users/123 → 403 для обычного пользователя."""
    async def override_require_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin required",
        )

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        client = TestClient(app)
        response = client.get("/users/123")

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()


def test_get_user_not_found():
    """GET /users/999999 → 404."""
    admin = create_fake_user(user_id=1, role=UserRole.ADMIN)

    async def override_require_admin():
        return admin

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=None)

            client = TestClient(app)
            response = client.get("/users/999999")

            assert response.status_code == 404
            assert response.json()["detail"] == "User not found"

    finally:
        app.dependency_overrides.clear()


def test_admin_update_user():
    """PATCH /users/123 → админ меняет username, role, is_active."""
    admin = create_fake_user(user_id=1, role=UserRole.ADMIN)
    target = create_fake_user(user_id=123, username="old_name", role=UserRole.USER)

    async def override_require_admin():
        return admin

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=target)

            client = TestClient(app)
            response = client.patch(
                "/users/123",
                json={
                    "username": "new_name",
                    "role": "admin",
                    "is_active": True,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "new_name"
            assert data["role"] == "admin"
            assert data["is_active"] is True

    finally:
        app.dependency_overrides.clear()


def test_regular_user_update_other_user_forbidden():
    """PATCH /users/123 → 403 для обычного пользователя."""
    async def override_require_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin required",
        )

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        client = TestClient(app)
        response = client.patch(
            "/users/123",
            json={"username": "hacker"},
        )

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()


def test_admin_delete_user():
    """DELETE /users/123 → админ деактивирует пользователя."""
    admin = create_fake_user(user_id=1, role=UserRole.ADMIN)
    target = create_fake_user(user_id=123, is_active=True)

    async def override_require_admin():
        return admin

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=target)

            client = TestClient(app)
            response = client.delete("/users/123")

            assert response.status_code == 200
            data = response.json()
            assert data["is_active"] is False

    finally:
        app.dependency_overrides.clear()


def test_regular_user_delete_forbidden():
    """DELETE /users/123 → 403 для обычного пользователя."""
    async def override_require_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin required",
        )

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        client = TestClient(app)
        response = client.delete("/users/123")

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()


def test_delete_user_not_found():
    """DELETE /users/999999 → 404."""
    admin = create_fake_user(user_id=1, role=UserRole.ADMIN)

    async def override_require_admin():
        return admin

    from backend.app.security.dependencies import require_admin
    app.dependency_overrides[require_admin] = override_require_admin
    setup_mock_db()

    try:
        with pytest.MonkeyPatch.context() as monkeypatch:
            setup_mock_repository(monkeypatch, user=None)

            client = TestClient(app)
            response = client.delete("/users/999999")

            assert response.status_code == 404
            assert response.json()["detail"] == "User not found"

    finally:
        app.dependency_overrides.clear()


def test_deactivated_user_cannot_access_me():
    """Деактивированный пользователь → GET /users/me → 401 Inactive user."""
    fake_user = create_fake_user(
        user_id=123,
        username="testuser",
        is_active=False,  # ← деактивирован
    )

    async def override_get_current_user():
        return fake_user

    from backend.app.security.dependencies import (
        get_current_user,
        get_current_active_user,
    )

    app.dependency_overrides[get_current_user] = override_get_current_user
    # НЕ переопределяем get_current_active_user — он должен сработать
    setup_mock_db()

    try:
        client = TestClient(app)
        response = client.get("/users/me")

        assert response.status_code == 401
        assert "Inactive user" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()