from fastapi import APIRouter, Request
from app.schemas.company_invitation import CompanyInvitationCreate, CompanyInvitationResponse, \
    CompanyInvitationListResponse
from app.routers.dependencies import UOWDep, CurrentUserDep, CompanyInvitationServiceDep

router = APIRouter(
    prefix="/company_invitations",
    tags=["Company Invitations"],
)


@router.post("/", response_model=CompanyInvitationResponse)
async def send_invitation(invitation: CompanyInvitationCreate, uow: UOWDep, current_user: CurrentUserDep,
                          service: CompanyInvitationServiceDep):
    return await service.send_invitation(uow, invitation, current_user.id)


@router.delete("/{invitation_id}", status_code=204)
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


@router.get("/", response_model=CompanyInvitationListResponse)
async def get_invitations(
        request: Request,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: CompanyInvitationServiceDep,
        skip: int = 0,
        limit: int = 10
):
    return await service.get_invitations(uow, current_user.id, skip, limit, str(request.url))
