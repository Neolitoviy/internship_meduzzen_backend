from datetime import datetime
from app.schemas.company_invitation import CompanyInvitationCreate, CompanyInvitationResponse, \
    CompanyInvitationListResponse, PaginationLinks
from app.utils.unitofwork import IUnitOfWork
from app.core.exceptions import CompanyPermissionError, InvitationNotFound


class CompanyInvitationService:
    @staticmethod
    async def send_invitation(uow: IUnitOfWork, invitation: CompanyInvitationCreate,
                              current_user_id: int) -> CompanyInvitationResponse:
        async with uow:
            company = await uow.companies.find_one(id=invitation.company_id)
            if company and company.owner_id == current_user_id:
                if invitation.invited_user_id == current_user_id:
                    raise CompanyPermissionError("You cannot send an invitation to yourself.")
                new_invitation = await uow.company_invitations.add_one(invitation.model_dump())
                return CompanyInvitationResponse.model_validate(new_invitation)
        raise CompanyPermissionError("You don't have permission to invite users to this company")

    @staticmethod
    async def cancel_invitation(uow: IUnitOfWork, invitation_id: int, current_user_id: int) -> None:
        async with uow:
            invitation = await uow.company_invitations.find_one(id=invitation_id)
            if not invitation:
                raise InvitationNotFound(f"Invitation with id {invitation_id} not found")
            company = await uow.companies.find_one(id=invitation.company_id)
            if company and company.owner_id == current_user_id:
                await uow.company_invitations.delete_one(invitation_id)
                return
        raise CompanyPermissionError("You don't have permission to cancel this invitation")

    @staticmethod
    async def accept_invitation(uow: IUnitOfWork, invitation_id: int, current_user_id: int) -> None:
        async with uow:
            invitation = await uow.company_invitations.find_one(id=invitation_id, invited_user_id=current_user_id)
            if not invitation:
                raise CompanyPermissionError("You don't have permission to accept this invitation")

            if await uow.company_members.find_one(company_id=invitation.company_id, user_id=current_user_id):
                raise CompanyPermissionError("You are already a member of this company")

            membership_data = {
                "company_id": invitation.company_id,
                "user_id": current_user_id,
                "created_at": datetime.utcnow(),
            }
            await uow.company_members.add_one(membership_data)
            invitation.status = 'accepted'

    @staticmethod
    async def decline_invitation(uow: IUnitOfWork, invitation_id: int, current_user_id: int) -> None:
        async with uow:
            invitation = await uow.company_invitations.find_one(id=invitation_id)
            if invitation and invitation.invited_user_id == current_user_id:
                invitation.status = 'declined'
                return
        raise CompanyPermissionError("You don't have permission to decline this invitation")

    @staticmethod
    async def get_invitations(uow: IUnitOfWork, user_id: int, skip: int, limit: int,
                              request_url: str) -> CompanyInvitationListResponse:
        async with uow:
            total_invitations = await uow.company_invitations.count_all(user_id=user_id)
            invitations = await uow.company_invitations.find_all(user_id=user_id, skip=skip, limit=limit)
            total_pages = (total_invitations + limit - 1) // limit
            current_page = (skip // limit) + 1

            base_url = request_url.split('?')[0]
            previous_page_url = f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}" if current_page > 1 else None
            next_page_url = f"{base_url}?skip={skip + limit}&limit={limit}" if current_page < total_pages else None

            return CompanyInvitationListResponse(
                total_pages=total_pages,
                current_page=current_page,
                invitations=[CompanyInvitationResponse.model_validate(invitation) for invitation in invitations],
                pagination=PaginationLinks(
                    previous=previous_page_url,
                    next=next_page_url
                )
            )