from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from faker import Faker
from fastapi.security import HTTPAuthorizationCredentials

from app.core.exceptions import EmailAlreadyExists, InvalidCredentials, PermissionDenied
from app.core.hashing import Hasher
from app.schemas.user import (
    UserCreate,
    UserCreateInput,
    UserInDB,
    UserUpdate,
    UserUpdateInput,
)
from app.services.user import UserService

faker = Faker()


@pytest.fixture
def mock_user():
    return UserInDB(
        id=1,
        email=faker.email(),
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        is_active=True,
        hashed_password=Hasher.get_password_hash("password"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_create_user_from_token(uow, mock_user):
    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test_token")
    email = mock_user.email
    uow.users.find_one_or_none.return_value = None

    new_user = mock_user

    with patch(
        "app.services.user.UserService.get_email_from_token", return_value=email
    ):
        with patch(
            "app.services.user.UserService.create_user", new_callable=AsyncMock
        ) as mock_create_user:
            mock_create_user.return_value = new_user
            user_in_db = await UserService.create_user_from_token(uow, token)

    assert user_in_db.email == email
    assert uow.users.find_one_or_none.called
    assert mock_create_user.called


@pytest.mark.asyncio
async def test_create_user(uow, mock_user):
    user_create_input = UserCreateInput(
        email=faker.email(),
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        password1="password",
        password2="password",
    )
    user_create = UserCreate.model_validate(user_create_input)

    mock_user = UserInDB(
        id=1,
        email=user_create.email,
        firstname=user_create.firstname,
        lastname=user_create.lastname,
        hashed_password=user_create.hashed_password,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    uow.users.find_one_or_none.return_value = None
    uow.users.add_one.return_value = mock_user

    user_response = await UserService.create_user(uow, user_create)

    assert user_response.email == user_create.email
    assert user_response.firstname == user_create.firstname
    assert user_response.lastname == user_create.lastname
    assert user_response.is_active == user_create.is_active
    assert user_response.is_superuser == user_create.is_superuser
    assert uow.users.add_one.called


@pytest.mark.asyncio
async def test_create_user_email_exists(uow, mock_user):
    user_create_input = UserCreateInput(
        email=mock_user.email,
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        password1="password",
        password2="password",
    )
    user_create = UserCreate.model_validate(user_create_input)

    uow.users.find_one_or_none.return_value = mock_user

    with pytest.raises(EmailAlreadyExists):
        await UserService.create_user(uow, user_create)


@pytest.mark.asyncio
async def test_get_user_by_id(uow, mock_user):
    user_id = 1

    uow.users.find_one.return_value = mock_user

    user_response = await UserService.get_user_by_id(uow, user_id)

    assert user_response.id == mock_user.id
    assert user_response.email == mock_user.email
    assert uow.users.find_one.called


@pytest.mark.asyncio
async def test_get_user_by_email(uow, mock_user):
    email = mock_user.email
    uow.users.find_one.return_value = mock_user

    user_in_db = await UserService.get_user_by_email(uow, email)

    assert user_in_db.email == email
    assert uow.users.find_one.called


@pytest.mark.asyncio
async def test_update_user(uow, mock_user):
    user_update_input = UserUpdateInput(
        firstname="UpdatedName",
        lastname="UpdatedLastName",
    )
    user_update = UserUpdate.model_validate(user_update_input)

    updated_user = UserInDB(
        id=mock_user.id,
        email=mock_user.email,
        firstname=user_update.firstname,
        lastname=user_update.lastname,
        hashed_password=mock_user.hashed_password,
        is_active=mock_user.is_active,
        is_superuser=mock_user.is_superuser,
        created_at=mock_user.created_at,
        updated_at=datetime.utcnow(),
    )

    uow.users.edit_one.return_value = updated_user

    updated_user_response = await UserService.update_user(
        uow, user_update, mock_user.id
    )

    assert updated_user_response.firstname == user_update.firstname
    assert updated_user_response.lastname == user_update.lastname
    assert uow.users.edit_one.called


@pytest.mark.asyncio
async def test_delete_user(uow, mock_user):
    user_id = mock_user.id
    updated_user_data = mock_user.model_dump()
    updated_user_data["is_active"] = False
    updated_user = UserInDB(**updated_user_data)

    uow.users.edit_one.return_value = updated_user

    await UserService.delete_user(uow, user_id)

    assert uow.users.edit_one.called
    assert updated_user.is_active is False


@pytest.mark.asyncio
async def test_authenticate_user(uow, mock_user):
    user_email = mock_user.email
    user_password = "password"

    uow.users.find_one.return_value = mock_user

    token = await UserService.authenticate_user(uow, user_email, user_password)

    assert token is not None
    assert "access_token" in token.dict()
    assert uow.users.find_one.called


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(uow, mock_user):
    email = mock_user.email
    password = "wrongpassword"
    uow.users.find_one.return_value = mock_user

    with pytest.raises(InvalidCredentials):
        await UserService.authenticate_user(uow, email, password)


@pytest.mark.asyncio
async def test_check_user_permission():
    user_id = 1
    current_user_id = 1

    await UserService.check_user_permission(user_id, current_user_id)

    with pytest.raises(PermissionDenied):
        await UserService.check_user_permission(user_id, 2)
