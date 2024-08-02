from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas.user import UserInDB
from app.services.auth import authenticate_and_get_user
from app.services.user import UserService
from app.utils.unitofwork import UnitOfWork


@pytest.fixture
def mock_user():
    return UserInDB(
        id=1,
        email="test@example.com",
        firstname="Test",
        lastname="User",
        is_active=True,
        hashed_password="hashedpassword",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_token():
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="mocktoken")


@pytest.mark.asyncio
async def test_authenticate_and_get_user(mock_user, mock_token):
    uow = AsyncMock(UnitOfWork)
    user_service = AsyncMock(UserService)
    user_service.create_user_from_token.return_value = mock_user

    authenticated_user = await authenticate_and_get_user(
        token=mock_token,
        uow=uow,
        user_service=user_service,
    )

    assert authenticated_user == mock_user
    user_service.create_user_from_token.assert_called_once_with(uow, mock_token)
