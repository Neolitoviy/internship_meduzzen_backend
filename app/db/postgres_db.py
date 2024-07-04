import logging
from app.db.database import engine
from sqlalchemy.sql import text


logger = logging.getLogger(__name__)


async def check_postgres_connection():
    try:
        logger.info("Attempting to connect to PostgreSQL")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL")
            return result.scalar() == 1
    except Exception as error:
        logger.error("Error connecting to PostgreSQL: %s", error)
        return str(error)