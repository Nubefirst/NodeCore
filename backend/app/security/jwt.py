from datetime import datetime, timedelta, timezone
import jwt

from backend.app.core.config import settings


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    to_encode.update({"exp": expires})

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


