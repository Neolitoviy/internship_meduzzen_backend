import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


async def check_postgres_connection(session: AsyncSession) -> bool:
    try:
        logger.info("Attempting to connect to PostgreSQL")
        result = await session.execute(text("SELECT 1"))
        logger.info("Successfully connected to PostgreSQL")
        return result.scalar() == 1
    except SQLAlchemyError as error:
        logger.error("Error connecting to PostgreSQL: %s", error)
        return str(error)
