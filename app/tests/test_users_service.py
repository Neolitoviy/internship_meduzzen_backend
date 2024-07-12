import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.users import UsersService
from app.schemas.users import UserCreate, UserUpdate, UserInDB
from app.utils.unitofwork import IUnitOfWork
from datetime import datetime


@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "firstname": "Test",
        "lastname": "User",
        "city": "Test City",
        "phone": "1234567890",
        "avatar": "http://example.com/avatar.png",
        "is_active": True,
        "is_superuser": False,
        "password1": "password",
        "password2": "password",
    }


async def test_create_user(user_data):
    uow = MagicMock(IUnitOfWork)
    uow.users.add_one = AsyncMock(return_value=1)
    uow.users.find_one = AsyncMock(return_value=UserInDB(
        id=1, hashed_password="hashed_password", created_at=datetime.utcnow(), updated_at=datetime.utcnow(), **user_data
    ))

    user = UserCreate(**user_data)
    result = await UsersService.create_user(uow, user)

    assert result.email == user_data["email"]
    assert result.firstname == user_data["firstname"]
    assert uow.users.add_one.called
    assert uow.commit.called


async def test_get_users(user_data):
    uow = MagicMock(IUnitOfWork)
    uow.users.find_all = AsyncMock(return_value=[
        UserInDB(id=1, hashed_password="hashed_password", created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                 **user_data)
    ])

    result = await UsersService.get_users(uow, skip=0, limit=10)

    assert len(result) == 1
    assert result[0].email == user_data["email"]


async def test_get_user_by_id(user_data):
    uow = MagicMock(IUnitOfWork)
    uow.users.find_one = AsyncMock(return_value=UserInDB(
        id=1, hashed_password="hashed_password", created_at=datetime.utcnow(), updated_at=datetime.utcnow(), **user_data
    ))

    result = await UsersService.get_user_by_id(uow, user_id=1)

    assert result.email == user_data["email"]
    assert result.id == 1


async def test_update_user(user_data):
    uow = MagicMock(IUnitOfWork)
    uow.users.edit_one = AsyncMock(return_value=user_data)
    uow.users.find_one = AsyncMock(return_value=UserInDB(
        id=1, hashed_password="hashed_password", created_at=datetime.utcnow(), updated_at=datetime.utcnow(), **user_data
    ))

    update_data = UserUpdate(firstname="Updated")
    result = await UsersService.update_user(uow, user_id=1, user=update_data)

    assert result.firstname == "Updated"
    assert uow.users.edit_one.called
    assert uow.commit.called


async def test_delete_user(user_data):
    uow = MagicMock(IUnitOfWork)
    uow.users.find_one = AsyncMock(return_value=UserInDB(
        id=1, hashed_password="hashed_password", created_at=datetime.utcnow(), updated_at=datetime.utcnow(), **user_data
    ))
    uow.users.delete_one = AsyncMock(return_value=user_data)

    result = await UsersService.delete_user(uow, user_id=1)

    assert result.email == user_data["email"]
    assert uow.users.delete_one.called
    assert uow.commit.called
