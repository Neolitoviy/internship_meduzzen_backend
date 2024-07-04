import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.sqlalchemy_database_url, echo=True, future=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
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
