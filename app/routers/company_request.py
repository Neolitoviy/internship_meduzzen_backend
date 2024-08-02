from fastapi import APIRouter, status

from app.routers.dependencies import CompanyRequestServiceDep, CurrentUserDep, UOWDep
from app.schemas.company_member import CompanyMemberResponse
from app.schemas.company_request import CompanyRequestResponse

router = APIRouter(
    prefix="/requests",
    tags=["Requests"],
)


@router.delete("/{request_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_request(
    request_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyRequestServiceDep,
):
    """
    Cancel a company request.

    Args:
        request_id (int): The ID of the request to cancel.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyRequestServiceDep): The company request service dependency.

    Returns:
        None
    """
    return await service.cancel_request(uow, request_id, current_user.id)


@router.post(
    "/{request_id}/accept",
    response_model=CompanyMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def accept_request(
    request_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyRequestServiceDep,
):
    """
    Accept a company request.

    Args:
        request_id (int): The ID of the request to accept.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyRequestServiceDep): The company request service dependency.

    Returns:
        CompanyMemberResponse: The newly created company member.
    """
    return await service.accept_request(uow, request_id, current_user.id)


@router.post(
    "/{request_id}/decline",
    response_model=CompanyRequestResponse,
    status_code=status.HTTP_200_OK,
)
async def decline_request(
    request_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyRequestServiceDep,
):
    """
    Decline a company request.

    Args:
        request_id (int): The ID of the request to decline.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyRequestServiceDep): The company request service dependency.

    Returns:
        CompanyRequestResponse: The declined request.
    """
    return await service.decline_request(uow, request_id, current_user.id)
