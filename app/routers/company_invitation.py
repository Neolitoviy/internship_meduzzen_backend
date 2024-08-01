from fastapi import APIRouter, status

from app.routers.dependencies import CompanyInvitationServiceDep, CurrentUserDep, UOWDep
from app.schemas.company_invitation import CompanyInvitationResponse
from app.schemas.company_member import CompanyMemberResponse

router = APIRouter(
    prefix="/invitations",
    tags=["Invitations"],
)


@router.delete("/{invitation_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_invitation(
    invitation_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyInvitationServiceDep,
):
    """
    Cancel a company invitation.

    Args:
        invitation_id (int): The ID of the invitation to cancel.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyInvitationServiceDep): The company invitation service dependency.

    Returns:
        None
    """
    return await service.cancel_invitation(uow, invitation_id, current_user.id)


@router.post(
    "/{invitation_id}/accept",
    response_model=CompanyMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def accept_invitation(
    invitation_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyInvitationServiceDep,
):
    """
    Accept a company invitation.

    Args:
        invitation_id (int): The ID of the invitation to accept.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyInvitationServiceDep): The company invitation service dependency.

    Returns:
        CompanyMemberResponse: The newly created company member.
    """
    return await service.accept_invitation(uow, invitation_id, current_user.id)


@router.post(
    "/{invitation_id}/decline",
    response_model=CompanyInvitationResponse,
    status_code=status.HTTP_200_OK,
)
async def decline_invitation(
    invitation_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyInvitationServiceDep,
):
    """
    Decline a company invitation.

    Args:
        invitation_id (int): The ID of the invitation to decline.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (CompanyInvitationServiceDep): The company invitation service dependency.

    Returns:
        CompanyInvitationResponse: The declined invitation.
    """
    return await service.decline_invitation(uow, invitation_id, current_user.id)
