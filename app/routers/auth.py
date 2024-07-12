from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from app.routers.dependencies import UserServiceDep, UOWDep
from app.schemas.auth import SignInRequest
from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.services.auth import authenticate_and_get_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

auth_scheme = HTTPBearer()


@router.post("/sign-in", response_model=Token)
async def sign_in(request: SignInRequest, uow: UOWDep, user_service: UserServiceDep) -> Token:
    token = await user_service.authenticate_user(uow, request.email, request.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return token


@router.get("/me", response_model=UserResponse)
async def get_authenticated_user(
        current_user: UserResponse = Depends(authenticate_and_get_user)) -> UserResponse:
    return current_user
