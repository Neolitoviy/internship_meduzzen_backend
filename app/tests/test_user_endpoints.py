import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


async def test_create_user(client: AsyncClient):
    user_data = {
        "email": "test@example.com",
        "firstname": "Test",
        "lastname": "User",
        "city": "Test City",
        "phone": "1234567890",
        "avatar": "http://example.com/avatar.png",
        "is_active": True,
        "is_superuser": False,
        "password1": "password",
        "password2": "password"
    }
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


async def test_get_users(client: AsyncClient):
    response = await client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json()["users"], list)


async def test_get_user(client: AsyncClient):
    user_id = 1  # змініть це на ID існуючого користувача
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


async def test_update_user(client: AsyncClient):
    user_id = 1
    update_data = {
        "firstname": "Updated",
        "lastname": "User"
    }
    response = await client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["firstname"] == "Updated"


async def test_delete_user(client: AsyncClient):
    user_id = 1
    response = await client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id
