import pytest
from app.schemas.users import UserCreate, UserUpdate
from app.services.users import UsersService
from app.utils.unitofwork import UnitOfWork
from app.models.users import Base
from app.db.database import engine


@pytest.fixture(scope="function", autouse=True)
async def setup_and_teardown_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def uow():
    return UnitOfWork()


async def test_add_user(uow):
    user_create = UserCreate(
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
        phone_number="1234567890",
        age=30,
        city="Test City"
    )
    user_response = await UsersService.add_user(uow, user_create)
    assert user_response.email == user_create.email
    assert user_response.username == user_create.username
    assert user_response.phone_number == user_create.phone_number


async def test_get_users(uow):
    user_create = UserCreate(
        email="testuser2@example.com",
        username="testuser2",
        password="testpassword",
        phone_number="0987654321",
        age=25,
        city="Test City"
    )
    await UsersService.add_user(uow, user_create)
    users = await UsersService.get_users(uow)
    assert len(users) > 0


async def test_get_user_by_id(uow):
    user_create = UserCreate(
        email="testuser3@example.com",
        username="testuser3",
        password="testpassword",
        phone_number="1111111111",
        age=35,
        city="Another City"
    )
    user_response = await UsersService.add_user(uow, user_create)
    user = await UsersService.get_user_by_id(uow, user_response.id)
    assert user.email == user_create.email


async def test_update_user(uow):
    user_create = UserCreate(
        email="testuser4@example.com",
        username="testuser4",
        password="testpassword",
        phone_number="2222222222",
        age=40,
        city="Yet Another City"
    )
    user_response = await UsersService.add_user(uow, user_create)
    user_update = UserUpdate(
        username="updateduser"
    )
    updated_user = await UsersService.update_user(uow, user_response.id, user_update)
    assert updated_user.username == user_update.username


async def test_delete_user(uow):
    user_create = UserCreate(
        email="testuser5@example.com",
        username="testuser5",
        password="testpassword",
        phone_number="3333333333",
        age=45,
        city="Delete City"
    )
    user_response = await UsersService.add_user(uow, user_create)
    deleted_user = await UsersService.delete_user(uow, user_response.id)
    assert deleted_user.id == user_response.id
