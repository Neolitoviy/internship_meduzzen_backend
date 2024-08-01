from sqlalchemy import RowMapping

from app.schemas.company_request import (
    CompanyRequestCreate,
    CompanyRequestListResponse,
    CompanyRequestResponse,
)
from app.services.company import CompanyService
from app.services.company_invitation import CompanyInvitationService
from app.services.user import UserService
from app.utils.pagination import paginate
from app.utils.unitofwork import IUnitOfWork


class CompanyRequestService:
    """
    Service class for managing company requests.

    Provides methods to request to join a company, cancel a request, accept or decline a request,
    and retrieve requests by user ID.
    """

    @staticmethod
    async def request_to_join_company(
        uow: IUnitOfWork, request: CompanyRequestCreate, current_user_id: int
    ) -> CompanyRequestResponse:
        """
        Create a request to join a company by user.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            request (CompanyRequestCreate): Data for creating the request.
            current_user_id (int): ID of the user making the request.

        Returns:
            CompanyRequestResponse: The created company request.
        """
        request_dict = request.model_dump()
        request_dict["requested_user_id"] = current_user_id
        async with uow:
            new_request = await uow.company_requests.add_one(request_dict)
            return CompanyRequestResponse.model_validate(new_request)

    @staticmethod
    async def cancel_request(
        uow: IUnitOfWork, request_id: int, current_user_id: int
    ) -> None:
        """
        Cancel a company request by requested user.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            request_id (int): ID of the request to be cancelled.
            current_user_id (int): ID of the user cancelling the request.

        Returns:
            None

        Raises:
            PermissionDenied: If the user didn't make this request.
        """
        async with uow:
            request = await uow.company_requests.find_one(id=request_id)
            await UserService.check_user_permission(
                request.requested_user_id, current_user_id
            )
            await uow.company_requests.delete_one(request_id)

    @staticmethod
    async def accept_request(
        uow: IUnitOfWork, request_id: int, current_user_id: int
    ) -> RowMapping:
        """
        Accept a company request, making the requested user a member of the company.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            request_id (int): ID of the request to be accepted.
            current_user_id (int): ID of the user accepting the request.

        Returns:
            RowMapping: The newly created company membership.

        Raises:
            CompanyPermissionError: If the user does not have permission to accept the request.
        """
        async with uow:
            request = await uow.company_requests.find_one(id=request_id)
            await CompanyService.check_company_owner(
                uow, request.company_id, current_user_id
            )
            await CompanyInvitationService.check_already_member(
                uow, request.company_id, request.requested_user_id
            )
            new_membership = await uow.company_members.add_one(
                {
                    "user_id": request.requested_user_id,
                    "company_id": request.company_id,
                }
            )
            request.status = "accepted"
            return new_membership

    @staticmethod
    async def decline_request(
        uow: IUnitOfWork, request_id: int, current_user_id: int
    ) -> CompanyRequestResponse:
        """
        Decline a company request by owner.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            request_id (int): ID of the request to be declined.
            current_user_id (int): ID of the user declining the request.

        Returns:
            CompanyRequestResponse: The declined company request.

        Raises:
            CompanyPermissionError: If the user isn't the owner.
        """
        async with uow:
            request = await uow.company_requests.find_one(id=request_id)
            await CompanyService.check_company_owner(
                uow, request.company_id, current_user_id
            )
            request.status = "declined"
            return CompanyRequestResponse.model_validate(request)

    @staticmethod
    async def get_requests_by_user_id(
        uow: IUnitOfWork, user_id: int, skip: int, limit: int, request_url: str
    ) -> CompanyRequestListResponse:
        """
        Retrieve company requests by user ID.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            user_id (int): ID of the user.
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.
            request_url (str): The URL for the request.

        Returns:
            CompanyRequestListResponse: Paginated list of company requests.
        """
        async with uow:
            total_requests = await uow.company_requests.count_all(user_id=user_id)
            requests = await uow.company_requests.find_all(
                user_id=user_id, skip=skip, limit=limit
            )

            requests_response = [
                CompanyRequestResponse.model_validate(request) for request in requests
            ]
            pagination_response = paginate(
                items=requests_response,
                total_items=total_requests,
                skip=skip,
                limit=limit,
                request_url=request_url,
            )

            return CompanyRequestListResponse(
                total_pages=pagination_response.total_pages,
                current_page=pagination_response.current_page,
                items=pagination_response.items,
                pagination=pagination_response.pagination,
            )
