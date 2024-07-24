import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.models.base import Base
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.company import CompanyService
from app.services.company_invitation import CompanyInvitationService
from app.services.company_member import CompanyMemberService
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

engine = create_async_engine(settings.sqlalchemy_database_url, future=True, echo=True)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session")
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield TestingSessionLocal
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def uow(db) -> AsyncGenerator[UnitOfWork, None]:
    async with UnitOfWork(session_factory=db) as uow:
        yield uow


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def current_user_id(uow: IUnitOfWork) -> int:
    user_service = UserService()
    user_create = UserCreate(
        email="testuser@example.com",
        firstname="Test",
        lastname="User",
        password1="password",
        password2="password",
    )
    user = await user_service.create_user(uow, user_create)
    return user.id


@pytest.fixture(scope="function")
async def current_user(uow: IUnitOfWork, user_service: UserService) -> User:
    user_create = UserCreate(
        email="test@example.com",
        firstname="Test",
        lastname="User",
        password1="password",
        password2="password",
    )
    user = await user_service.create_user(uow, user_create)
    return user


@pytest.fixture(scope="function")
async def user_service(uow: IUnitOfWork) -> UserService:
    return UserService()


@pytest.fixture
async def member_service(uow: IUnitOfWork) -> CompanyMemberService:
    service = CompanyMemberService()
    yield service


@pytest.fixture
def company_service() -> CompanyService:
    return CompanyService()


@pytest.fixture
def invitation_service() -> CompanyInvitationService:
    return CompanyInvitationService()


@pytest.fixture
async def create_test_user(uow: IUnitOfWork, user_service: UserService):
    async def _create_test_user(email: str, password: str = "password"):
        user_create = UserCreate(
            email=email,
            firstname="Test",
            lastname="User",
            password1=password,
            password2=password,
        )
        user = await user_service.create_user(uow, user_create)
        token_response = await user_service.authenticate_user(
            uow, email=email, password=password
        )
        return user, token_response.access_token

    return _create_test_user
