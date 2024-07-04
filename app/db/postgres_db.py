from app.db.database import engine
from sqlalchemy.sql import text


async def check_postgres_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as error:
        return str(error)