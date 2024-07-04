from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


async def check_postgres_connection(session: AsyncSession) -> bool:
    try:
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except SQLAlchemyError as error:
        return str(error)
