import pytest
from httpx import AsyncClient
from app.main import app
from app.db.database import async_session
from app.models.users import Base
from datetime import datetime, timezone


@pytest.fixture(scope="function", autouse=True)
async def setup_and_teardown_database():
    async with async_session() as session:
        async with session.begin():
            await session.run_sync(Base.metadata.create_all)
        yield
        async with session.begin():
            await session.run_sync(Base.metadata.drop_all)


async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword",
            "phone_number": "1234567890",
            "age": 30,
            "city": "Test City",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        response = await ac.post("/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert data["phone_number"] == payload["phone_number"]
        assert data["age"] == payload["age"]
        assert data["city"] == payload["city"]


async def test_get_users():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


async def test_get_user_by_id():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First, create a user to ensure there is a user to get
        payload = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword",
            "phone_number": "1234567890",
            "age": 30,
            "city": "Test City",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        create_response = await ac.post("/users", json=payload)
        user_id = create_response.json()["id"]

        response = await ac.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert data["phone_number"] == payload["phone_number"]
        assert data["age"] == payload["age"]
        assert data["city"] == payload["city"]


async def test_update_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First, create a user to ensure there is a user to update
        payload = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword",
            "phone_number": "1234567890",
            "age": 30,
            "city": "Test City",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        create_response = await ac.post("/users", json=payload)
        user_id = create_response.json()["id"]

        update_payload = {
            "username": "updateduser"
        }
        response = await ac.put(f"/users/{user_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == update_payload["username"]


async def test_delete_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First, create a user to ensure there is a user to delete
        payload = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword",
            "phone_number": "1234567890",
            "age": 30,
            "city": "Test City",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        create_response = await ac.post("/users", json=payload)
        user_id = create_response.json()["id"]

        response = await ac.delete(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
