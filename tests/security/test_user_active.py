import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from backend.app.security.dependencies import get_current_active_user


@pytest.mark.asyncio
async def test_get_current_active_user_active():
    """1. Активный пользователь → возвращает пользователя."""
    # 1. Создаём фейкового пользователя с is_active=True
    fake_user = MagicMock()
    fake_user.is_active = True

    # 2. Вызываем функцию
    result = await get_current_active_user(fake_user)

    # 3. Проверяем результат
    assert result is fake_user


@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    """2. Неактивный пользователь → 401 'Inactive user'."""
    # 1. Создаём фейкового пользователя с is_active=False
    fake_user = MagicMock()
    fake_user.is_active = False

    # 2. Ожидаем исключение
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(fake_user)

    # 3. Проверяем ошибку
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Inactive user"