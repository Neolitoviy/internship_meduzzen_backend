import asyncio_redis
from app.core.config import get_settings

settings = get_settings()


async def check_redis_connection():
    try:
        connection = await asyncio_redis.Connection.create(host=settings.redis_host, port=settings.redis_port)
        response = await connection.ping()
        connection.close()
        return response.status == 'PONG'
    except Exception as error:
        return str(error)
