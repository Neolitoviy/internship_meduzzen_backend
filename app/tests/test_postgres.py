import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import text

from app.db.database import async_session, engine
from app.db.postgres_db import check_postgres_connection

# Creating a base model for declarative ORM style
Base = declarative_base()


# Fixture for setting up the database
@pytest.fixture
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Fixture for creating a session
@pytest.fixture
async def get_test_session():
    async with async_session() as session:
        yield session


async def create_test_table(session: AsyncSession):
    try:
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL
            )
        """))
        await session.commit()
    except SQLAlchemyError as error:
        await session.rollback()
        raise error


# Test to check PostgreSQL connection
@pytest.mark.asyncio
async def test_postgres_connection(get_test_session):
    session = await get_test_session.__anext__()
    assert await check_postgres_connection(session) is True


# Test to create a table
@pytest.mark.asyncio
async def test_create_table(get_test_session):
    session = await get_test_session.__anext__()
    await create_test_table(session)
    result = await session.execute(text("""
        SELECT to_regclass('public.test_table') IS NOT NULL
    """))
    table_exists = result.scalar()
    assert table_exists is True