import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check_postgres():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health/postgres")
    assert response.status_code == 200
    assert response.json() == {"postgresql": "connected"}
