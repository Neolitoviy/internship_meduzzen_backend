import pytest
from httpx import AsyncClient
from app.services.user import UserService
from app.schemas.auth import SignInRequest
from app.schemas.token import Token
from app.utils.unitofwork import IUnitOfWork


async def test_authenticate_and_get_user(ac: AsyncClient, uow: IUnitOfWork):
    user_service = UserService()

    user_create = SignInRequest(
        email="test_auth@example.com",
        password="password"
    )

    async with uow:
        created_user = await user_service.create_user(uow, user_create)

        sign_in_request = SignInRequest(
            email=created_user.email,
            password=created_user.password
        )
        token: Token = await user_service.authenticate_user(uow, sign_in_request.email, sign_in_request.password)

    headers = {"Authorization": f"Bearer {token.access_token}"}
    response = await ac.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == user_create.email


async def test_invalid_token(ac: AsyncClient):
    headers = {"Authorization": "Bearer invalid_token"}
    response = await ac.get("/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not Found or Bad Request"
