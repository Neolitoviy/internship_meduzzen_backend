from fastapi import APIRouter, status

from app.routers.dependencies import CompanyInvitationServiceDep, CurrentUserDep, UOWDep
from app.schemas.company_invitation import CompanyInvitationResponse
from app.schemas.company_member import CompanyMemberResponse

router = APIRouter(
    prefix="/invitation",
    tags=["Invitation"],
)


@router.delete("/{invitation_id}/cancel", status_code=204)
async def cancel_invitation(
    invitation_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: CompanyInvitationServiceDep,
):
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
    return await service.decline_invitation(uow, invitation_id, current_user.id)
