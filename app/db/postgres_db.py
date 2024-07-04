import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_postgres_connection(session: AsyncSession) -> bool:
    try:
        logger.info("Attempting to connect to PostgreSQL")
        result = await session.execute(select(1))
        logger.info("Successfully connected to PostgreSQL")
        return result.scalar() == 1
    except SQLAlchemyError as error:
        logger.error("Error connecting to PostgreSQL: %s", error)
        return str(error)
