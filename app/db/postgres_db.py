import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_postgres_connection(session: AsyncSession) -> bool:
    """
    Check the connection to the PostgreSQL database.

    This function executes a simple SELECT statement to verify the connection to the
    PostgreSQL database. If the connection is successful, it logs the success and returns True.
    If an error occurs, it logs the error and returns False.

    Args:
        session (AsyncSession): The active database session.

    Returns:
        bool: True if the connection is successful, False otherwise.

    Raises:
        SQLAlchemyError: If an error occurs during the session execution.
    """
    try:
        logger.info("Attempting to connect to PostgreSQL")
        result = await session.execute(select(1))
        logger.info("Successfully connected to PostgreSQL")
        return result.scalar() == 1
    except SQLAlchemyError as error:
        logger.error("Error connecting to PostgreSQL: %s", error)
        return False
