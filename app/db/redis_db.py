import logging

import asyncio_redis

from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_redis_client():
    """
    Establish a connection to the Redis server.

    This function creates and returns a connection to the Redis server using
    the configuration settings provided in the application settings.

    Returns:
        asyncio_redis.Connection: An active Redis connection.

    Raises:
        asyncio_redis.exceptions.ConnectionError: If there is an issue establishing the connection.
    """
    return await asyncio_redis.Connection.create(
        host=settings.redis_host, port=settings.redis_port
    )


async def check_redis_connection():
    """
    Check the connection to the Redis server.

    This function attempts to connect to the Redis server and send a PING command
    to verify the connection. If the connection is successful, it logs the success
    and returns True. If an error occurs, it logs the error and returns False.

    Returns:
        bool: True if the connection is successful and the PING response is "PONG", Error otherwise.

    Raises:
        Exception: If an error occurs during the connection or PING operation.
    """
    try:
        logger.info("Attempting to connect to Redis")
        connection = await get_redis_client()
        response = await connection.ping()
        connection.close()
        logger.info("Successfully connected to Redis")
        return response.status == "PONG"
    except Exception as error:
        logger.error("Error connecting to Redis: %s", error)
        return str(error)