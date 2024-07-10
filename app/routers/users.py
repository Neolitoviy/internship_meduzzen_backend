from typing import List
from fastapi import APIRouter, HTTPException, Request
from app.routers.dependencies import UOWDep, UserServiceDep
from app.schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse
import logging
from app.core.logging_config import logging_config

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("", response_model=UserResponse)
async def create_user(user: UserCreate, uow: UOWDep, user_service: UserServiceDep):
    try:
        user = await user_service.create_user(uow, user)
        return user
    except ValueError as e:
        logger.error("Error creating user: %s", e)
        raise HTTPException(status_code=400, detail=f"Error creating user: {e}")
    except Exception as e:
        logger.error("Error creating user: %s", e)
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")


@router.get("", response_model=UserListResponse)
async def get_users(request: Request, uow: UOWDep, user_service: UserServiceDep, skip: int = 0, limit: int = 10):
    try:
        request_url = str(request.url)
        users_response = await user_service.get_users(uow, skip, limit, request_url)
        return users_response
    except ValueError as e:
        logger.error("Error fetching users: %s", e)
        raise HTTPException(status_code=400, detail=f"Error fetching users: {e}")
    except Exception as e:
        logger.error("Error fetching users: %s", e)
        raise HTTPException(status_code=500, detail=f"Error fetching users: {e}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, uow: UOWDep, user_service: UserServiceDep):
    try:
        user = await user_service.get_user_by_id(uow, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        logger.error("Error fetching user: %s", e)
        raise HTTPException(status_code=400, detail=f"Error fetching user: {e}")
    except Exception as e:
        logger.error("Error fetching user: %s", e)
        raise HTTPException(status_code=500, detail=f"Error fetching user: {e}")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, uow: UOWDep, user_service: UserServiceDep):
    try:
        user = await user_service.update_user(uow, user_id, user)
        return user
    except ValueError as e:
        logger.error("Error updating user: %s", e)
        raise HTTPException(status_code=400, detail=f"Error updating user: {e}")
    except Exception as e:
        logger.error("Error updating user: %s", e)
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, uow: UOWDep, user_service: UserServiceDep):
    try:
        user = await user_service.delete_user(uow, user_id)
        return user
    except ValueError as e:
        logger.error("Error deleting user: %s", e)
        raise HTTPException(status_code=400, detail=f"Error deleting user: {e}")
    except Exception as e:
        logger.error("Error deleting user: %s", e)
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")
