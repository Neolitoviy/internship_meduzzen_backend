import asyncio
import pytest
from typing import AsyncGenerator
from starlette.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.main import app
from app.models.base import Base
from app.utils.unitofwork import UnitOfWork

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(settings.sqlalchemy_database_url, future=True, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


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
