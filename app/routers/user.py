import logging

from fastapi import APIRouter, Request, status

from app.core.logging_config import logging_config
from app.routers.dependencies import CurrentUserDep, UOWDep, UserServiceDep
from app.schemas.user import (
    UserCreate,
    UserCreateInput,
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserUpdateInput,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateInput, uow: UOWDep, user_service: UserServiceDep):
    return await user_service.create_user(uow, UserCreate.model_validate(user))


@router.get("/", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def get_users(
    request: Request,
    uow: UOWDep,
    user_service: UserServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await user_service.get_users(uow, skip, limit, str(request.url))


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, uow: UOWDep, user_service: UserServiceDep):
    return await user_service.get_user_by_id(uow, user_id)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    user: UserUpdateInput,
    uow: UOWDep,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    return await user_service.update_user(
        uow, user_id, UserUpdate.model_validate(user), current_user.id
    )


@router.delete(
    "/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def delete_user(
    user_id: int,
    uow: UOWDep,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    return await user_service.delete_user(uow, user_id, current_user.id)
