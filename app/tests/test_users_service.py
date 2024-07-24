import pytest
from httpx import AsyncClient

from app.core.exceptions import UserNotFound
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork


async def test_create_user(ac: AsyncClient, uow: IUnitOfWork):
    user_service = UserService()

    user_create = UserCreate(
        email="test@example.com",
        firstname="John",
        lastname="Doe",
        password1="password",
        password2="password",
    )

    async with uow:
        user = await user_service.create_user(uow, user_create)

    assert user.email == user_create.email
    assert user.firstname == user_create.firstname
    assert user.lastname == user_create.lastname
    assert user.is_active is True
    assert user.is_superuser is False


async def test_get_user_by_id(ac: AsyncClient, uow: IUnitOfWork):
    user_service = UserService()

    user_create = UserCreate(
        email="test2@example.com",
        firstname="Jane",
        lastname="Doe",
        password1="password",
        password2="password",
    )

    async with uow:
        created_user = await user_service.create_user(uow, user_create)
        retrieved_user = await user_service.get_user_by_id(uow, created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.email == user_create.email


async def test_update_user(ac: AsyncClient, uow: IUnitOfWork):
    user_service = UserService()

    user_create = UserCreate(
        email="test3@example.com",
        firstname="Alice",
        lastname="Smith",
        password1="password",
        password2="password",
    )

    async with uow:
        created_user = await user_service.create_user(uow, user_create)

        user_update = UserUpdate(firstname="AliceUpdated", lastname="SmithUpdated")
        updated_user = await user_service.update_user(
            uow, created_user.id, user_update, created_user.id
        )

    assert updated_user.firstname == user_update.firstname
    assert updated_user.lastname == user_update.lastname


async def test_delete_user(ac: AsyncClient, uow: IUnitOfWork):
    user_service = UserService()

    user_create = UserCreate(
        email="test4@example.com",
        firstname="Bob",
        lastname="Brown",
        password1="password",
        password2="password",
    )

    async with uow:
        created_user = await user_service.create_user(uow, user_create)
        deleted_user = await user_service.delete_user(
            uow, created_user.id, created_user.id
        )

    assert deleted_user.email == user_create.email

    async with uow:
        with pytest.raises(UserNotFound):
            await user_service.get_user_by_id(uow, created_user.id)
