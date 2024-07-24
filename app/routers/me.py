from typing import List

from fastapi import APIRouter, Depends, Request
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


@router.post("/sign-in", response_model=Token)
async def sign_in(
    request: SignInRequest, uow: UOWDep, user_service: UserServiceDep
) -> Token:
    token = await user_service.authenticate_user(uow, request.email, request.password)
    if token is None:
        raise InvalidCredentials("Token is None")
    return token


@router.get("/", response_model=UserResponse)
async def get_authenticated_user(
    current_user: UserResponse = Depends(authenticate_and_get_user),
) -> UserResponse:
    return current_user


@router.get("/requests", response_model=CompanyRequestListResponse)
async def get_requests(
    request: Request,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyRequestServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_requests_by_user_id(
        uow, current_user.id, skip, limit, str(request.url)
    )


@router.get("/invites", response_model=CompanyInvitationListResponse)
async def get_invitations(
    request: Request,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyInvitationServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_invitations(
        uow, current_user.id, skip, limit, str(request.url)
    )


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_all_my_notifications(
    uow: UOWDep,
    current_user: CurrentUserDep,
    notification_service: NotificationServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await notification_service.get_user_notifications(
        uow, current_user.id, skip, limit
    )


@router.put(
    "/notifications/{notification_id}/read", response_model=NotificationResponse
)
async def read_notification_by_id(
    notification_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    notification_service: NotificationServiceDep,
):
    return await notification_service.mark_notification_as_read(
        uow, notification_id, current_user.id
    )
