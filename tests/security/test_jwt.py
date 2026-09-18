import pytest
import jwt
import json
import base64
from fastapi.testclient import TestClient
from backend.app.security.jwt import create_refresh_token,decode_refresh_token,create_access_token, decode_access_token
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from backend.app.main import app
from backend.app.dependencies.database import get_db
from backend.app.repositories.user import UserRepository
from backend.app.security.password import hash_password
from backend.app.core.config import settings


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "123"})
    assert isinstance(token, str)


def test_create_access_token_has_three_parts():
    token = create_access_token({"sub": "123"})
    parts = token.split(".")

    assert len(parts) == 3


def test_create_access_token_has_expected_header():
    import jwt

    token = create_access_token({"sub": "123"})
    header = jwt.get_unverified_header(token)

    assert header["alg"] == "HS256"
    assert header["typ"] == "JWT"


def test_create_access_token_contains_sub():
    import jwt

    token = create_access_token({"sub": "123", "email": "test@example.com"})
    payload = jwt.decode(token, options={"verify_signature": False})

    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"


def test_create_access_token_has_exp():
    import jwt

    token = create_access_token({"sub": "123"})
    payload = jwt.decode(token, options={"verify_signature": False})

    assert "exp" in payload
    assert isinstance(payload["exp"], int)


def test_decode_valid_token_returns_payload():
    token = create_access_token({"sub": "123", "email": "test@example.com"})
    payload = decode_access_token(token)
    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload


def test_decode_wrong_secret_raises_error(monkeypatch):
    token = create_access_token({"sub": "123"})

    monkeypatch.setattr(settings, "jwt_secret_key", "wrong_secret_key")

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_decode_tampered_token_raises_error():

    token = create_access_token({"sub": "123"})
    header, payload, signature = token.split(".")

    payload_decoded = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
    payload_dict = json.loads(payload_decoded)
    payload_dict["sub"] = "999"

    new_payload = base64.urlsafe_b64encode(
        json.dumps(payload_dict).encode()
    ).decode().rstrip("=")

    tampered_token = f"{header}.{new_payload}.{signature}"

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(tampered_token)


def test_decode_expired_token_raises_error():
    expired_token = jwt.encode(
        {"sub": "123", "exp": 0},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)


def test_decode_invalid_token_raises_error():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("not.a.jwt")


def test_access_token_contains_type_access():
    token = create_access_token({"sub": "123"})
    payload = jwt.decode(token, options={"verify_signature": False})

    assert payload["type"] == "access"


def test_refresh_token_contains_type_refresh():
    token = create_refresh_token({"sub": "123"})
    payload = jwt.decode(token, options={"verify_signature": False})

    assert payload["type"] == "refresh"


def test_access_token_cannot_be_decoded_as_refresh():
    access_token = create_access_token({"sub": "123"})

    with pytest.raises(ValueError):
        decode_refresh_token(access_token)


def test_refresh_token_cannot_be_decoded_as_access():
    refresh_token = create_refresh_token({"sub": "123"})

    with pytest.raises(ValueError):
        decode_access_token(refresh_token)


def test_refresh_token_has_7_days_expiration():
    """Проверяет, что exp находится примерно через 7 дней от текущего момента."""
    token = create_refresh_token({"sub": "123"})
    payload = jwt.decode(token, options={"verify_signature": False})

    exp = payload["exp"]
    now = datetime.now(timezone.utc).timestamp()
    expected = now + (7 * 24 * 60 * 60)


    assert abs(exp - expected) < 60





@pytest.fixture
def client():
    """Фикстура для создания тестового клиента."""
    return TestClient(app)


def test_refresh_valid_token(client):
    """1. Валидный refresh → 200 + новый access_token."""
    refresh_token = create_refresh_token({"sub": "123"})

    fake_user = MagicMock()
    fake_user.id = 123
    fake_user.is_active = True

    mock_repository = MagicMock()
    mock_repository.get_by_id = AsyncMock(return_value=fake_user)

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
                "/auth/refresh",
                json={"refresh_token": refresh_token},
            )

            assert response.status_code == 200
            data = response.json()
            payload = decode_access_token(data["access_token"])
            assert payload["sub"] == "123"
            assert "access_token" in data
            assert data["token_type"] == "bearer"

            mock_repository.get_by_id.assert_awaited_once_with(123)

    finally:
        app.dependency_overrides.clear()



def test_refresh_with_access_token(client):
    """2. Access token вместо refresh → 401."""
    access_token = create_access_token({"sub": "123"})

    async def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": access_token},
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()



def test_refresh_with_invalid_token(client):
    """3. Полностью невалидный токен → 401."""
    async def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "not.a.jwt"},
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()



def test_refresh_with_expired_token(client):
    """4. Истёкший refresh → 401."""
    expired_token = jwt.encode(
        {"sub": "123", "exp": 0, "type": "refresh"},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    async def override_get_db():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": expired_token},
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()



def test_refresh_with_nonexistent_user(client):
    """5. Refresh с несуществующим sub → 401."""
    refresh_token = create_refresh_token({"sub": "99999"})

    mock_repository = MagicMock()
    mock_repository.get_by_id = AsyncMock(return_value=None)

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
                "/auth/refresh",
                json={"refresh_token": refresh_token},
            )

            assert response.status_code == 401
            assert "Invalid refresh token" in response.json()["detail"]

            mock_repository.get_by_id.assert_awaited_once_with(99999)

    finally:
        app.dependency_overrides.clear()


def test_refresh_with_inactive_user(client):
    """6. Refresh неактивного пользователя → 401."""
    refresh_token = create_refresh_token({"sub": "123"})


    fake_user = MagicMock()
    fake_user.id = 123
    fake_user.is_active = False

    mock_repository = MagicMock()
    mock_repository.get_by_id = AsyncMock(return_value=fake_user)


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
                "/auth/refresh",
                json={"refresh_token": refresh_token},
            )

            assert response.status_code == 401
            assert "Invalid refresh token" in response.json()["detail"]

            mock_repository.get_by_id.assert_awaited_once_with(123)

    finally:
        app.dependency_overrides.clear()