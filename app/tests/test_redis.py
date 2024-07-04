import asyncio_redis
import pytest

from app.core.config import settings
from app.db.redis_db import check_redis_connection


@pytest.mark.asyncio
async def test_redis_connection():
    result = await check_redis_connection()
    assert result == True, f"Expected True but got {result}"


@pytest.mark.asyncio
async def test_redis_set_get():
    connection = await asyncio_redis.Connection.create(host=settings.redis_host, port=settings.redis_port)
    await connection.set("test_key", "test_value")
    value = await connection.get("test_key")
    await connection.delete(["test_key"])
    connection.close()
    assert value == "test_value", f"Expected 'test_value' but got {value}"


@pytest.mark.asyncio
async def test_redis_delete():
    connection = await asyncio_redis.Connection.create(host=settings.redis_host, port=settings.redis_port)
    await connection.set("test_key", "test_value")
    await connection.delete(["test_key"])
    value = await connection.get("test_key")
    connection.close()
    assert value is None, f"Expected None but got {value}"
