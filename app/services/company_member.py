from typing import Optional

from app.schemas.company_member import CompanyMemberListResponse, CompanyMemberResponse
from app.services.company import CompanyService
from app.utils.pagination import paginate
from app.utils.unitofwork import IUnitOfWork


class CompanyMemberService:
    """
    Service class to manage company members.

    Provides methods to add, remove, and manage company members, including
    handling administrative roles.
    """

    @staticmethod
    async def remove_member(
        uow: IUnitOfWork, member_id: int, current_user_id: int
    ) -> None:
        """
        Remove a member from a company.

        Args:
            uow (IUnitOfWork): Unit of work to handle database transactions.
            member_id (int): ID of the member to be removed.
            current_user_id (int): ID of the current user requesting the removal.

        Raises:
            CompanyPermissionError: If the current user is not the owner of the company.
        """
        async with uow:
            member = await uow.company_members.find_one(id=member_id)
            await CompanyService.check_company_owner(
                uow, member.company_id, current_user_id
            )
            await uow.company_members.delete_one(member_id)

    @staticmethod
    async def leave_company(
        uow: IUnitOfWork, company_id: int, current_user_id: int
    ) -> None:
        """
        Allow a user to leave a company.

        Args:
            uow (IUnitOfWork): Unit of work to handle database transactions.
            company_id (int): ID of the company to leave.
            current_user_id (int): ID of the current user leaving the company.
        """
        async with uow:
            member = await uow.company_members.find_one(
                user_id=current_user_id, company_id=company_id
            )
            await uow.company_members.delete_one(member.id)

    @staticmethod
    async def get_memberships(
        uow: IUnitOfWork,
        user_id: int,
        company_id: int,
        skip: int,
        limit: int,
        request_url: str,
        is_admin: Optional[bool] = None,
    ) -> CompanyMemberListResponse:
        """
        Get a list of company members with pagination.

        Args:
            uow (IUnitOfWork): Unit of work to handle database transactions.
            user_id (int): ID of the current user requesting the list.
            company_id (int): ID of the company.
            skip (int): Number of items to skip.
            limit (int): Maximum number of items to return.
            request_url (str): URL of the current request for pagination links.
            is_admin (Optional[bool]): Filter by admin status if provided.

        Returns:
            CompanyMemberListResponse: Paginated response with list of company members.

        Raises:
            CompanyPermissionError: If the current user does not have permission to view the members.
        """
        async with uow:
            await CompanyService.check_company_permission(uow, company_id, user_id)

            if is_admin is not None:
                total_members = await uow.company_members.count_all(
                    company_id=company_id, is_admin=is_admin
                )
                members = await uow.company_members.find_all(
                    skip=skip,
                    limit=limit,
                    company_id=company_id,
                    is_admin=is_admin,
                )
            else:
                total_members = await uow.company_members.count_all(
                    company_id=company_id
                )
                members = await uow.company_members.find_all(
                    skip=skip, limit=limit, company_id=company_id
                )

            members_response = [
                CompanyMemberResponse.model_validate(member) for member in members
            ]
            pagination_response = paginate(
                items=members_response,
                total_items=total_members,
                skip=skip,
                limit=limit,
                request_url=request_url,
            )

            return CompanyMemberListResponse(
                total_pages=pagination_response.total_pages,
                current_page=pagination_response.current_page,
                items=pagination_response.items,
                pagination=pagination_response.pagination,
            )

    @staticmethod
    async def appoint_admin(
        uow: IUnitOfWork, company_id: int, user_id: int, current_user_id: int
    ) -> None:
        """
        Appoint a member as an admin.

        Args:
            uow (IUnitOfWork): Unit of work to handle database transactions.
            company_id (int): ID of the company.
            user_id (int): ID of the user to be appointed as admin.
            current_user_id (int): ID of the current user requesting the appointment.

        Raises:
            CompanyPermissionError: If the current user is not the owner of the company.
        """
        async with uow:
            await CompanyService.check_company_owner(uow, company_id, current_user_id)
            member = await uow.company_members.find_one(
                company_id=company_id, user_id=user_id
            )
            member.is_admin = True

    @staticmethod
    async def remove_admin(
        uow: IUnitOfWork, company_id: int, user_id: int, current_user_id: int
    ) -> None:
        """
        Remove a member from the admin role.

        Args:
            uow (IUnitOfWork): Unit of work to handle database transactions.
            company_id (int): ID of the company.
            user_id (int): ID of the user to be removed from the admin role.
            current_user_id (int): ID of the current user requesting the removal.

        Raises:
            CompanyPermissionError: If the current user is not the owner of the company.
        """
        async with uow:
            await CompanyService.check_company_owner(uow, company_id, current_user_id)
            member = await uow.company_members.find_one(
                company_id=company_id, user_id=user_id
            )
            member.is_admin = False
