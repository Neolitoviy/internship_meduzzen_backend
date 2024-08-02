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
    """
    Service for handling company invitations.
    """

    @staticmethod
    async def send_invitation(
        uow: IUnitOfWork,
        invitation: CompanyInvitationCreate,
        current_user_id: int,
    ) -> CompanyInvitationResponse:
        """
        Send a company invitation from owner to user(not self).

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            invitation (CompanyInvitationCreate): Data for the invitation.
            current_user_id (int): ID of the current user.

        Returns:
            CompanyInvitationResponse: The created invitation response.
        """
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
        """
        Cancel a company invitation. Access : only company owner.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            invitation_id (int): ID of the invitation to cancel.
            current_user_id (int): ID of the current user.
        """
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
        """
        Accept a company invitation. Access : only invited user. Not company member.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            invitation_id (int): ID of the invitation to accept.
            current_user_id (int): ID of the current user.

        Returns:
            RowMapping: The new membership data.
        """
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
        """
        Decline a company invitation. Access : only invited user.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            invitation_id (int): ID of the invitation to decline.
            current_user_id (int): ID of the current user.

        Returns:
            CompanyInvitationResponse: The declined invitation response.
        """
        async with uow:
            invitation = await uow.company_invitations.find_one(id=invitation_id)
            await UserService.check_user_permission(
                invitation.invited_user_id, current_user_id
            )
            invitation.status = "declined"
            return CompanyInvitationResponse.model_validate(invitation)

    @staticmethod
    async def get_invitations(
        uow: IUnitOfWork, current_user_id: int, skip: int, limit: int, request_url: str
    ) -> CompanyInvitationListResponse:
        """
        Get a list of invitations for a user.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            current_user_id (int): ID of the current user.
            skip (int): Number of items to skip.
            limit (int): Number of items to return.
            request_url (str): The request URL for pagination.

        Returns:
            CompanyInvitationListResponse: The list of invitations with pagination.
        """
        async with uow:
            total_invitations = await uow.company_invitations.count_all(user_id=current_user_id)
            invitations = await uow.company_invitations.find_all(
                user_id=current_user_id, skip=skip, limit=limit
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
        """
        Check if the invitation is not being sent to oneself.

        Args:
            invited_user_id (int): ID of the invited user.
            current_user_id (int): ID of the current user.

        Raises:
            CompanyPermissionError: If the user tries to invite themselves.
        """
        if invited_user_id == current_user_id:
            raise CompanyPermissionError("You cannot send an invitation to yourself.")

    @staticmethod
    async def check_already_member(
        uow: IUnitOfWork, company_id: int, current_user_id: int
    ) -> None:
        """
        Check if the user is already a member of the company.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            company_id (int): ID of the company.
            current_user_id (int): ID of the current user.

        Raises:
            CompanyPermissionError: If the user is already a member of the company.
        """
        if await uow.company_members.find_one(
            company_id=company_id, user_id=current_user_id
        ):
            raise CompanyPermissionError("You are already a member of this company")
