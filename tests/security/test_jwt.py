import jwt
import pytest
import json
import base64
from backend.app.security.jwt import create_access_token, decode_access_token
from datetime import datetime, timedelta, timezone
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