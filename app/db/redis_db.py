import logging

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_redis_client():
    return redis.Redis(
        host=settings.redis_host,
        port=int(settings.redis_port),
        ssl=True
    )


async def check_redis_connection():
    try:
        logger.info("Attempting to connect to Redis")
        connection = await get_redis_client()
        response = await connection.ping()
        await connection.close()
        logger.info("Successfully connected to Redis")
        return response
    except Exception as error:
        logger.error("Error connecting to Redis: %s", error)
        return str(error)
