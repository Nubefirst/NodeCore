from unittest.mock import MagicMock

import pytest

from scripts.create_admin import get_admin_password


def test_get_admin_password_from_env(monkeypatch):
    """Проверяет, что при заданном NODECORE_ADMIN_PASSWORD функция возвращает его."""
    monkeypatch.setenv("NODECORE_ADMIN_PASSWORD", "test-only-password")

    result = get_admin_password()

    assert result == "test-only-password"


def test_get_admin_password_interactive(monkeypatch):
    monkeypatch.delenv("NODECORE_ADMIN_PASSWORD", raising=False)

    mock_getpass = MagicMock(return_value="test-only-password")
    monkeypatch.setattr(
        "scripts.create_admin.getpass.getpass",
        mock_getpass,
    )

    result = get_admin_password()

    assert result == "test-only-password"

    mock_getpass.assert_called_once()


def test_get_admin_password_empty_env(monkeypatch):
    """Проверяет, что пустая переменная окружения → ValueError, без запроса пароля."""
    monkeypatch.setenv("NODECORE_ADMIN_PASSWORD", "")

    mock_getpass = MagicMock()
    monkeypatch.setattr(
        "scripts.create_admin.getpass.getpass",
        mock_getpass,
    )

    with pytest.raises(ValueError):
        get_admin_password()

    mock_getpass.assert_not_called()


def test_get_admin_password_empty_input(monkeypatch):
    """Проверяет, что пустой ввод → ValueError."""
    monkeypatch.delenv("NODECORE_ADMIN_PASSWORD", raising=False)

    mock_getpass = MagicMock(return_value="")
    monkeypatch.setattr(
        "scripts.create_admin.getpass.getpass",
        mock_getpass,
    )

    with pytest.raises(ValueError):
        get_admin_password()

    mock_getpass.assert_called_once()


def test_get_admin_password_whitespace_input(monkeypatch):
    """Проверяет, что ввод из пробелов → ValueError."""
    monkeypatch.delenv("NODECORE_ADMIN_PASSWORD", raising=False)

    mock_getpass = MagicMock(return_value="   ")
    monkeypatch.setattr(
        "scripts.create_admin.getpass.getpass",
        mock_getpass,
    )

    with pytest.raises(ValueError):
        get_admin_password()

    mock_getpass.assert_called_once()
