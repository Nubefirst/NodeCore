import pytest

from backend.app.security.jwt import create_access_token

def test_create_access_token_returns_string():
    """Проверяет, что функция возвращает строку."""
    token = create_access_token({"sub": "123"})
    assert isinstance(token, str)


def test_create_access_token_has_three_parts():
    """Проверяет, что токен состоит из трёх частей."""
    token = create_access_token({"sub": "123"})
    parts = token.split(".")

    assert len(parts) == 3


def test_create_access_token_has_expected_header():
    """Проверяет, что header содержит правильный алгоритм."""
    import jwt

    token = create_access_token({"sub": "123"})
    header = jwt.get_unverified_header(token)

    assert header["alg"] == "HS256"
    assert header["typ"] == "JWT"


def test_create_access_token_contains_sub():
    """Проверяет, что payload содержит переданные данные."""
    import jwt

    token = create_access_token({"sub": "123", "email": "test@example.com"})
    payload = jwt.decode(token, options={"verify_signature": False})

    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"


def test_create_access_token_has_exp():
    """Проверяет, что в токене есть поле exp (время истечения)."""
    import jwt

    token = create_access_token({"sub": "123"})
    payload = jwt.decode(token, options={"verify_signature": False})

    assert "exp" in payload
    assert isinstance(payload["exp"], int)