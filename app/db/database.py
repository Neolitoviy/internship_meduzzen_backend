import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Create a logger instance
logger = logging.getLogger(__name__)

# Create an asynchronous engine connected to the database URL specified in settings
engine = create_async_engine(settings.sqlalchemy_database_url, echo=True, future=True)

# Create an asynchronous session maker with the engine
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """
    Provides an asynchronous database session.

    This function is used for healthcheck endpoint for Postgres

    Yields:
        AsyncSession: The database session.

    Raises:
        SQLAlchemyError: If an error occurs during the session, it is logged and the transaction is rolled back.
    """
    async with async_session() as session:
        try:
            logger.info("Session started")
            yield session
            await session.commit()
            logger.info("Session committed")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Session rollback due to: %s", e)
            raise
