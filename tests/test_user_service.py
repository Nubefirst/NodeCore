from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from backend.app.core.exceptions import ConflictError
from backend.app.main import internal_error_handler
from backend.app.schemas.user import UserCreate
from backend.app.services.user import UserService

from loguru import logger


@pytest.mark.asyncio
async def test_create_user_handles_username_integrity_error():
    repository = MagicMock()
    repository.get_by_username = AsyncMock(return_value=None)
    repository.session.rollback = AsyncMock()

    orig_error = MagicMock()
    orig_error.diag.constraint_name = "users_username_key"

    integrity_error = IntegrityError(
        "INSERT INTO users",
        {},
        orig_error,
    )

    repository.create = AsyncMock(side_effect=integrity_error)
    service = UserService(repository)
    user_data = UserCreate(
        username="danil",
        password="12345678",
    )

    with pytest.raises(ConflictError, match="Username already exists"):
        await service.create(user_data)

    repository.session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_reraises_other_integrity_error():
    repository = MagicMock()
    repository.get_by_username = AsyncMock(return_value=None)
    repository.session.rollback = AsyncMock()

    orig_error = MagicMock()
    orig_error.diag.constraint_name = "some_other_constraint"

    integrity_error = IntegrityError(
        "INSERT INTO users",
        {},
        orig_error,
    )

    repository.create = AsyncMock(side_effect=integrity_error)
    service = UserService(repository)
    user_data = UserCreate(
        username="danil",
        password="12345678",
    )

    with pytest.raises(IntegrityError):
        await service.create(user_data)

    repository.session.rollback.assert_awaited_once()


def test_unexpected_error_returns_500():
    test_app = FastAPI()
    test_app.add_exception_handler(Exception, internal_error_handler)

    @test_app.get("/test-internal-error")
    async def test_internal_error():
        raise ValueError("Secret internal error")

    client = TestClient(
        test_app,
        raise_server_exceptions=False,
    )

    log_messages = []
    handler_id = logger.add(
        lambda message: log_messages.append(str(message)),
        level="ERROR",
        format="{level} | {message}",
    )

    try:
        response = client.get("/test-internal-error")
    finally:
        logger.remove(handler_id)

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": "Internal server error",
        }
    }

    assert any(
        "Unhandled exception: GET /test-internal-error" in message
        for message in log_messages
    )
    assert any(
        "ValueError: Secret internal error" in message
        for message in log_messages
    )


@pytest.mark.asyncio
async def test_create_user_reraises_integrity_error_without_constraint_name():
    repository = MagicMock()
    repository.get_by_username = AsyncMock(return_value=None)
    repository.session.rollback = AsyncMock()

    orig_error = MagicMock(spec=[])

    integrity_error = IntegrityError(
        "INSERT INTO users",
        {},
        orig_error,
    )

    repository.create = AsyncMock(side_effect=integrity_error)
    service = UserService(repository)
    user_data = UserCreate(
        username="danil",
        password="12345678",
    )

    with pytest.raises(IntegrityError):
        await service.create(user_data)

    repository.session.rollback.assert_awaited_once()
    