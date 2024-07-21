from fastapi import APIRouter, Request
from app.routers.dependencies import UOWDep, CurrentUserDep, CompanyInvitationServiceDep

router = APIRouter(
    prefix="/invitation",
    tags=["Invitation"],
)


@router.delete("/{invitation_id}/cancel", status_code=204)
async def cancel_invitation(invitation_id: int, uow: UOWDep, current_user: CurrentUserDep,
                            service: CompanyInvitationServiceDep):
    return await service.cancel_invitation(uow, invitation_id, current_user.id)


@router.post("/{invitation_id}/accept", status_code=204)
async def accept_invitation(invitation_id: int, uow: UOWDep, current_user: CurrentUserDep,
                            service: CompanyInvitationServiceDep):
    return await service.accept_invitation(uow, invitation_id, current_user.id)


@router.post("/{invitation_id}/deny", status_code=204)
async def decline_invitation(invitation_id: int, uow: UOWDep, current_user: CurrentUserDep,
                             service: CompanyInvitationServiceDep):
    return await service.decline_invitation(uow, invitation_id, current_user.id)