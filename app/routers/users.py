from typing import List
from fastapi import APIRouter, HTTPException, Request

from app.core.exceptions import UserCreationError, UserFetchError, UserNotFoundError, UserUpdateError, UserDeletionError
from app.routers.dependencies import UOWDep, UserServiceDep
from app.schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse
import logging
from app.core.logging_config import logging_config

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, uow: UOWDep, user_service: UserServiceDep):
    try:
        return await user_service.create_user(uow, user)
    except UserCreationError as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=UserListResponse)
async def get_users(request: Request, uow: UOWDep, user_service: UserServiceDep, skip: int = 0, limit: int = 10):
    try:
        return await user_service.get_users(uow, skip, limit, str(request.url))
    except UserFetchError as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, uow: UOWDep, user_service: UserServiceDep):
    try:
        user = await user_service.get_user_by_id(uow, user_id)
        if not user:
            raise UserNotFoundError("User not found")
        return user
    except UserNotFoundError as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, uow: UOWDep, user_service: UserServiceDep):
    try:
        return await user_service.update_user(uow, user_id, user)
    except UserUpdateError as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, uow: UOWDep, user_service: UserServiceDep):
    try:
        return await user_service.delete_user(uow, user_id)
    except UserDeletionError as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
