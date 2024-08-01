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
    """
    Create a new user.

    Args:
        user (UserCreateInput): The data required to create a new user.
        uow (UOWDep): The unit of work dependency.
        user_service (UserServiceDep): The user service dependency.

    Returns:
        UserResponse: The created user.
    """
    return await user_service.create_user(uow, UserCreate.model_validate(user))


@router.get("/", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def get_users(
    request: Request,
    uow: UOWDep,
    user_service: UserServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve a list of users with pagination.

    Args:
        request (Request): The request object.
        uow (UOWDep): The unit of work dependency.
        user_service (UserServiceDep): The user service dependency.
        skip (int): Number of records to skip for pagination. Default is 0.
        limit (int): Maximum number of records to return. Default is 10.

    Returns:
        UserListResponse: A paginated list of users.
    """
    return await user_service.get_users(uow, skip, limit, str(request.url))


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, uow: UOWDep, user_service: UserServiceDep):
    """
    Retrieve a user by ID.

    Args:
        user_id (int): The ID of the user to retrieve.
        uow (UOWDep): The unit of work dependency.
        user_service (UserServiceDep): The user service dependency.

    Returns:
        UserResponse: The retrieved user.
    """
    return await user_service.get_user_by_id(uow, user_id)


@router.put("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user: UserUpdateInput,
    uow: UOWDep,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    """
    Update the current user's information.

    Args:
        user (UserUpdateInput): The data to update the user with.
        uow (UOWDep): The unit of work dependency.
        user_service (UserServiceDep): The user service dependency.
        current_user (CurrentUserDep): The current authenticated user.

    Returns:
        UserResponse: The updated user.
    """
    return await user_service.update_user(
        uow, UserUpdate.model_validate(user), current_user.id
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    uow: UOWDep,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    """
    Delete the current user's account.

    Args:
        uow (UOWDep): The unit of work dependency.
        user_service (UserServiceDep): The user service dependency.
        current_user (CurrentUserDep): The current authenticated user.

    Returns:
        None
    """
    return await user_service.delete_user(uow, current_user.id)
