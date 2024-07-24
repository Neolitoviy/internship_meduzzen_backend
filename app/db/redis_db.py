import logging

import asyncio_redis

from app.core.config import settings

logger = logging.getLogger(__name__)


async def check_redis_connection():
    try:
        logger.info("Attempting to connect to Redis")
        connection = await asyncio_redis.Connection.create(
            host=settings.redis_host, port=settings.redis_port
        )
        response = await connection.ping()
        connection.close()
        logger.info("Successfully connected to Redis")
        return response.status == "PONG"
    except Exception as error:
        logger.error("Error connecting to Redis: %s", error)
        return str(error)
