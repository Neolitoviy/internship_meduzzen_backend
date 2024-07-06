from typing import List
from fastapi import APIRouter, HTTPException
from app.routers.dependencies import UOWDep
from app.schemas.users import UserCreate, UserUpdate, UserResponse
from app.services.users import UsersService
import logging
from app.core.logging_config import logging_config

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("", response_model=UserResponse)
async def add_user(user: UserCreate, uow: UOWDep):
    try:
        user = await UsersService().add_user(uow, user)
        return user
    except ValueError as e:
        logger.error("Error adding user: %s", e)
        raise HTTPException(status_code=400, detail=f"Error adding user: {e}")
    except Exception as e:
        logger.error("Error adding user: %s", e)
        raise HTTPException(status_code=500, detail=f"Error adding user: {e}")


@router.get("", response_model=List[UserResponse])
async def get_users(uow: UOWDep):
    try:
        users = await UsersService().get_users(uow)
        return users
    except ValueError as e:
        logger.error("Error fetching users: %s", e)
        raise HTTPException(status_code=400, detail=f"Error fetching users: {e}")
    except Exception as e:
        logger.error("Error fetching users: %s", e)
        raise HTTPException(status_code=500, detail=f"Error fetching users: {e}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, uow: UOWDep):
    try:
        user = await UsersService().get_user_by_id(uow, user_id)
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
async def update_user(user_id: int, user: UserUpdate, uow: UOWDep):
    try:
        user = await UsersService().update_user(uow, user_id, user)
        return user
    except ValueError as e:
        logger.error("Error updating user: %s", e)
        raise HTTPException(status_code=400, detail=f"Error updating user: {e}")
    except Exception as e:
        logger.error("Error updating user: %s", e)
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, uow: UOWDep):
    try:
        user = await UsersService().delete_user(uow, user_id)
        return user
    except ValueError as e:
        logger.error("Error deleting user: %s", e)
        raise HTTPException(status_code=400, detail=f"Error deleting user: {e}")
    except Exception as e:
        logger.error("Error deleting user: %s", e)
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")
