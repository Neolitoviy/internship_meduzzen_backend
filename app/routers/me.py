from typing import List

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer

from app.core.exceptions import InvalidCredentials
from app.routers.dependencies import (
    CompanyInvitationServiceDep,
    CompanyRequestServiceDep,
    CurrentUserDep,
    NotificationServiceDep,
    UOWDep,
    UserServiceDep,
)
from app.schemas.auth import SignInRequest
from app.schemas.company_invitation import CompanyInvitationListResponse
from app.schemas.company_request import CompanyRequestListResponse
from app.schemas.notification import NotificationResponse
from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.services.auth import authenticate_and_get_user

router = APIRouter(
    prefix="/me",
    tags=["Me"],
)

auth_scheme = HTTPBearer()


@router.post("/sign-in", response_model=Token, status_code=status.HTTP_200_OK)
async def sign_in(
    request: SignInRequest, uow: UOWDep, user_service: UserServiceDep
) -> Token:
    """
    Sign in a user and generate an authentication token.

    Args:
        request (SignInRequest): The sign-in request containing email and password.
        uow (UOWDep): The unit of work dependency.
        user_service (UserServiceDep): The user service dependency.

    Returns:
        Token: The generated authentication token.

    Raises:
        InvalidCredentials: If authentication fails.
    """
    token = await user_service.authenticate_user(uow, request.email, request.password)
    if token is None:
        raise InvalidCredentials("Token is None")
    return token


@router.get("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_authenticated_user(
    current_user: UserResponse = Depends(authenticate_and_get_user),
) -> UserResponse:
    """
    Get the authenticated user's details.

    Args:
        current_user (UserResponse): The current authenticated user.

    Returns:
        UserResponse: The authenticated user's details.
    """
    return current_user


@router.get(
    "/requests",
    response_model=CompanyRequestListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_requests(
    request: Request,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyRequestServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    """
    Get the authenticated user's company requests.

    Args:
        request (Request): The request object.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyRequestServiceDep): The company request service dependency.
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.

    Returns:
        CompanyRequestListResponse: The list of company requests.
    """
    return await service.get_requests_by_user_id(
        uow, current_user.id, skip, limit, str(request.url)
    )


@router.get(
    "/invites",
    response_model=CompanyInvitationListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_invitations(
    request: Request,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyInvitationServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    """
    Get the authenticated user's company invitations.

    Args:
        request (Request): The request object.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyInvitationServiceDep): The company invitation service dependency.
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.

    Returns:
        CompanyInvitationListResponse: The list of company invitations.
    """
    return await service.get_invitations(
        uow, current_user.id, skip, limit, str(request.url)
    )


@router.get(
    "/notifications",
    response_model=List[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_my_notifications(
    uow: UOWDep,
    current_user: CurrentUserDep,
    notification_service: NotificationServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    """
    Get all notifications for the authenticated user.

    Args:
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        notification_service (NotificationServiceDep): The notification service dependency.
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.

    Returns:
        List[NotificationResponse]: The list of notifications.
    """
    return await notification_service.get_user_notifications(
        uow, current_user.id, skip, limit
    )


@router.put(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def read_notification_by_id(
    notification_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    notification_service: NotificationServiceDep,
):
    """
    Mark a notification as read by its ID.

    Args:
        notification_id (int): The ID of the notification to mark as read.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        notification_service (NotificationServiceDep): The notification service dependency.

    Returns:
        NotificationResponse: The updated notification.
    """
    return await notification_service.mark_notification_as_read(
        uow, notification_id, current_user.id
    )
