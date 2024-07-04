from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


async def check_postgres_connection(session: AsyncSession) -> bool:
    try:
        result = await session.execute(select(1))
        return result.scalar() == 1
    except SQLAlchemyError as error:
        return str(error)