from fastapi import APIRouter, Request
from app.routers.dependencies import UOWDep, UserServiceDep, CurrentUserDep
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
import logging
from app.core.logging_config import logging_config

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, uow: UOWDep, user_service: UserServiceDep):
    return await user_service.create_user(uow, user)


@router.get("/", response_model=UserListResponse)
async def get_users(request: Request, uow: UOWDep, user_service: UserServiceDep, skip: int = 0, limit: int = 10):
    return await user_service.get_users(uow, skip, limit, str(request.url))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, uow: UOWDep, user_service: UserServiceDep):
    return await user_service.get_user_by_id(uow, user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, uow: UOWDep, user_service: UserServiceDep, current_user: CurrentUserDep):
    return await user_service.update_user(uow, user_id, user, current_user.id)


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, uow: UOWDep, user_service: UserServiceDep, current_user: CurrentUserDep):
    return await user_service.delete_user(uow, user_id, current_user.id)
