import logging

from fastapi import APIRouter, Request, status

from app.core.logging_config import logging_config
from app.routers.dependencies import (
    CompanyInvitationServiceDep,
    CompanyMemberServiceDep,
    CompanyRequestServiceDep,
    CompanyServiceDep,
    CurrentUserDep,
    UOWDep,
)
from app.schemas.company import (
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.schemas.company_invitation import (
    CompanyInvitationCreate,
    CompanyInvitationResponse,
)
from app.schemas.company_member import CompanyMemberListResponse
from app.schemas.company_request import CompanyRequestCreate, CompanyRequestResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyCreate,
    uow: UOWDep,
    current_user: CurrentUserDep,
    company_service: CompanyServiceDep,
):
    """
    Create a new company.

    Args:
        company (CompanyCreate): The data to create a new company.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        company_service (CompanyServiceDep): The company service dependency.

    Returns:
        CompanyResponse: The created company.
    """
    return await company_service.create_company(uow, company, current_user.id)


@router.get("/", response_model=CompanyListResponse, status_code=status.HTTP_200_OK)
async def get_companies(
    request: Request,
    uow: UOWDep,
    current_user: CurrentUserDep,
    company_service: CompanyServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve a list of companies with pagination.

    Args:
        request (Request): The request object.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        company_service (CompanyServiceDep): The company service dependency.
        skip (int): Number of records to skip for pagination. Default is 0.
        limit (int): Maximum number of records to return. Default is 10.

    Returns:
        CompanyListResponse: A paginated list of companies.
    """
    return await company_service.get_companies(
        uow, skip, limit, str(request.url), current_user.id
    )


@router.get(
    "/{company_id}", response_model=CompanyResponse, status_code=status.HTTP_200_OK
)
async def get_company(
    company_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    company_service: CompanyServiceDep,
):
    """
    Retrieve a company by ID.

    Args:
        company_id (int): The ID of the company to retrieve.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        company_service (CompanyServiceDep): The company service dependency.

    Returns:
        CompanyResponse: The retrieved company.
    """
    return await company_service.get_company_by_id(uow, company_id, current_user.id)


@router.put(
    "/{company_id}", response_model=CompanyResponse, status_code=status.HTTP_200_OK
)
async def update_company(
    company_id: int,
    company: CompanyUpdate,
    uow: UOWDep,
    current_user: CurrentUserDep,
    company_service: CompanyServiceDep,
):
    """
    Update a company.

    Args:
        company_id (int): The ID of the company to update.
        company (CompanyUpdate): The data to update the company with.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        company_service (CompanyServiceDep): The company service dependency.

    Returns:
        CompanyResponse: The updated company.
    """
    return await company_service.update_company(
        uow, company_id, company, current_user.id
    )


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company(
    company_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    company_service: CompanyServiceDep,
):
    """
    Delete a company.

    Args:
        company_id (int): The ID of the company to delete.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        company_service (CompanyServiceDep): The company service dependency.

    Returns:
        None
    """
    return await company_service.delete_company(uow, company_id, current_user.id)


@router.post(
    "/{company_id}/join",
    response_model=CompanyRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_to_join_company(
    company_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyRequestServiceDep,
):
    """
    Request to join a company.

    Args:
        company_id (int): The ID of the company to join.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyRequestServiceDep): The company request service dependency.

    Returns:
        CompanyRequestResponse: The created company request.
    """
    request = CompanyRequestCreate(company_id=company_id)
    return await service.request_to_join_company(uow, request, current_user.id)


@router.post(
    "/{company_id}/invite/{user_id}",
    response_model=CompanyInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_user_to_company(
    company_id: int,
    user_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyInvitationServiceDep,
):
    """
    Invite a user to join a company.

    Args:
        company_id (int): The ID of the company.
        user_id (int): The ID of the user to invite.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyInvitationServiceDep): The company invitation service dependency.

    Returns:
        CompanyInvitationResponse: The created company invitation.
    """
    invitation = CompanyInvitationCreate(company_id=company_id, invited_user_id=user_id)
    return await service.send_invitation(uow, invitation, current_user.id)


@router.post("/{company_id}/leave", status_code=status.HTTP_200_OK)
async def leave_company(
    company_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyMemberServiceDep,
):
    """
    Leave a company.

    Args:
        company_id (int): The ID of the company to leave.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyMemberServiceDep): The company member service dependency.

    Returns:
        dict: A message indicating the user has successfully left the company.
    """
    await service.leave_company(uow, company_id, current_user.id)
    return {"detail": "Successfully left the company"}


@router.get(
    "/{company_id}/members",
    response_model=CompanyMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_memberships_by_company_id(
    request: Request,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyMemberServiceDep,
    company_id: int,
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve a list of company members with pagination.

    Args:
        request (Request): The request object.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyMemberServiceDep): The company member service dependency.
        company_id (int): The ID of the company.
        skip (int): Number of records to skip for pagination. Default is 0.
        limit (int): Maximum number of records to return. Default is 10.

    Returns:
        CompanyMemberListResponse: A paginated list of company members.
    """
    return await service.get_memberships(
        uow, current_user.id, company_id, skip, limit, str(request.url)
    )


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyMemberServiceDep,
):
    """
    Remove a member from the company.

    Args:
        member_id (int): The ID of the member to remove.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyMemberServiceDep): The company member service dependency.

    Returns:
        None
    """
    return await service.remove_member(uow, member_id, current_user.id)


@router.post("/{company_id}/admins/{user_id}/appoint", status_code=status.HTTP_200_OK)
async def appoint_admin(
    company_id: int,
    user_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyMemberServiceDep,
):
    """
    Appoint a user as an admin of the company.

    Args:
        company_id (int): The ID of the company.
        user_id (int): The ID of the user to appoint as admin.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyMemberServiceDep): The company member service dependency.

    Returns:
        dict: A message indicating the user has been appointed as admin.
    """
    await service.appoint_admin(uow, company_id, user_id, current_user.id)
    return {"detail": "User appointed as admin successfully"}


@router.post("/{company_id}/admins/{user_id}/remove", status_code=status.HTTP_200_OK)
async def remove_admin(
    company_id: int,
    user_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyMemberServiceDep,
):
    """
    Remove a user from the admin role of the company.

    Args:
        company_id (int): The ID of the company.
        user_id (int): The ID of the user to remove as admin.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyMemberServiceDep): The company member service dependency.

    Returns:
        dict: A message indicating the user has been removed as admin.
    """
    await service.remove_admin(uow, company_id, user_id, current_user.id)
    return {"detail": "User removed as admin successfully"}


@router.get(
    "/{company_id}/admins",
    response_model=CompanyMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_admins(
    request: Request,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyMemberServiceDep,
    company_id: int,
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve a list of company admins with pagination.

    Args:
        request (Request): The request object.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyMemberServiceDep): The company member service dependency.
        company_id (int): The ID of the company.
        skip (int): Number of records to skip for pagination. Default is 0.
        limit (int): Maximum number of records to return. Default is 10.

    Returns:
        CompanyMemberListResponse: A paginated list of company admins.
    """
    return await service.get_memberships(
        uow,
        current_user.id,
        company_id,
        skip,
        limit,
        str(request.url),
        is_admin=True,
    )
