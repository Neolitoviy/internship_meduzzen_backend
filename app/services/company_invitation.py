from datetime import datetime

from sqlalchemy import RowMapping

from app.core.exceptions import CompanyPermissionError
from app.schemas.company_invitation import (
    CompanyInvitationCreate,
    CompanyInvitationListResponse,
    CompanyInvitationResponse,
)
from app.services.company import CompanyService
from app.services.user import UserService
from app.utils.pagination import paginate
from app.utils.unitofwork import IUnitOfWork


class CompanyInvitationService:
    @staticmethod
    async def send_invitation(
        uow: IUnitOfWork,
        invitation: CompanyInvitationCreate,
        current_user_id: int,
    ) -> CompanyInvitationResponse:
        async with uow:
            await CompanyService.check_company_owner(
                uow, invitation.company_id, current_user_id
            )
            await CompanyInvitationService.check_not_self_invitation(
                invitation.invited_user_id, current_user_id
            )
            new_invitation = await uow.company_invitations.add_one(
                invitation.model_dump()
            )
            return CompanyInvitationResponse.model_validate(new_invitation)

    @staticmethod
    async def cancel_invitation(
        uow: IUnitOfWork, invitation_id: int, current_user_id: int
    ) -> None:
        async with uow:
            invitation = await uow.company_invitations.find_one(id=invitation_id)
            await CompanyService.check_company_owner(
                uow, invitation.company_id, current_user_id
            )
            await uow.company_invitations.delete_one(invitation_id)

    @staticmethod
    async def accept_invitation(
        uow: IUnitOfWork, invitation_id: int, current_user_id: int
    ) -> RowMapping:
        async with uow:
            invitation = await uow.company_invitations.find_one(
                id=invitation_id, invited_user_id=current_user_id
            )
            await CompanyInvitationService.check_already_member(
                uow, invitation.company_id, current_user_id
            )
            membership_data = {
                "company_id": invitation.company_id,
                "user_id": current_user_id,
                "created_at": datetime.utcnow(),
            }
            new_membership = await uow.company_members.add_one(membership_data)
            invitation.status = "accepted"
            return new_membership

    @staticmethod
    async def decline_invitation(
        uow: IUnitOfWork, invitation_id: int, current_user_id: int
    ) -> CompanyInvitationResponse:
        async with uow:
            invitation = await uow.company_invitations.find_one(id=invitation_id)
            await UserService.check_user_permission(
                invitation.invited_user_id, current_user_id
            )
            invitation.status = "declined"
            return CompanyInvitationResponse.model_validate(invitation)

    @staticmethod
    async def get_invitations(
        uow: IUnitOfWork, user_id: int, skip: int, limit: int, request_url: str
    ) -> CompanyInvitationListResponse:
        async with uow:
            total_invitations = await uow.company_invitations.count_all(user_id=user_id)
            invitations = await uow.company_invitations.find_all(
                user_id=user_id, skip=skip, limit=limit
            )

            invitations_response = [
                CompanyInvitationResponse.model_validate(invitation)
                for invitation in invitations
            ]
            pagination_response = paginate(
                items=invitations_response,
                total_items=total_invitations,
                skip=skip,
                limit=limit,
                request_url=request_url,
            )

            return CompanyInvitationListResponse(
                total_pages=pagination_response.total_pages,
                current_page=pagination_response.current_page,
                items=pagination_response.items,
                pagination=pagination_response.pagination,
            )

    @staticmethod
    async def check_not_self_invitation(
        invited_user_id: int, current_user_id: int
    ) -> None:
        if invited_user_id == current_user_id:
            raise CompanyPermissionError("You cannot send an invitation to yourself.")

    @staticmethod
    async def check_already_member(
        uow: IUnitOfWork, company_id: int, current_user_id: int
    ) -> None:
        if await uow.company_members.find_one(
            company_id=company_id, user_id=current_user_id
        ):
            raise CompanyPermissionError("You are already a member of this company")
