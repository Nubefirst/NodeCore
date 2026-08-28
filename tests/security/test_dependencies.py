import pytest
import jwt
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from backend.app.security.dependencies import get_current_user
from backend.app.security.jwt import create_access_token, decode_access_token
from backend.app.core.config import settings


@pytest.mark.asyncio
async def test_get_current_user_valid_token_user_exists():
    """Валидный токен + существующий пользователь → возвращает пользователя."""
    token = create_access_token({"sub": "123"})
    fake_user = MagicMock()
    fake_user.id = 123

    mock_repository = MagicMock()
    mock_repository.get_by_id = AsyncMock(return_value=fake_user)

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "backend.app.security.dependencies.UserRepository",
            lambda db: mock_repository,
        )

        user = await get_current_user(token, MagicMock())

        assert user is fake_user
        mock_repository.get_by_id.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_get_current_user_missing_sub():
    """1. JWT без sub → 401 'missing sub'."""
    token = create_access_token({"email": "test@example.com"})  # ← без sub

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "backend.app.security.dependencies.UserRepository",
            lambda db: MagicMock(),
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, MagicMock())

        assert exc_info.value.status_code == 401
        assert "missing 'sub'" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_invalid_sub_type():
    """2. sub не число → 401 'must be a valid integer'."""
    token = create_access_token({"sub": "abc"})  # ← не число

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "backend.app.security.dependencies.UserRepository",
            lambda db: MagicMock(),
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, MagicMock())

        assert exc_info.value.status_code == 401
        assert "must be a valid integer" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    """3. Пользователь не найден → 401 'User not found'."""
    token = create_access_token({"sub": "123"})

    mock_repository = MagicMock()
    mock_repository.get_by_id = AsyncMock(return_value=None)  # ← пользователь не найден

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "backend.app.security.dependencies.UserRepository",
            lambda db: mock_repository,
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, MagicMock())

        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail
        mock_repository.get_by_id.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    """4. Просроченный JWT → 401 'Token expired'."""
    # Создаём токен с exp = 0 (уже просрочен)
    expired_token = jwt.encode(
        {"sub": "123", "exp": 0},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "backend.app.security.dependencies.UserRepository",
            lambda db: MagicMock(),
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(expired_token, MagicMock())

        assert exc_info.value.status_code == 401
        assert "Token expired" in exc_info.value.detail