from sqlalchemy import RowMapping

from app.schemas.company_request import (
    CompanyRequestCreate,
    CompanyRequestListResponse,
    CompanyRequestResponse,
    PaginationLinks,
)
from app.services.company import CompanyService
from app.services.company_invitation import CompanyInvitationService
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork


class CompanyRequestService:
    @staticmethod
    async def request_to_join_company(
        uow: IUnitOfWork, request: CompanyRequestCreate, current_user_id: int
    ) -> CompanyRequestResponse:
        request_dict = request.model_dump()
        request_dict["requested_user_id"] = current_user_id
        async with uow:
            new_request = await uow.company_requests.add_one(request_dict)
            return CompanyRequestResponse.model_validate(new_request)

    @staticmethod
    async def cancel_request(
        uow: IUnitOfWork, request_id: int, current_user_id: int
    ) -> None:
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
        async with uow:
            total_requests = await uow.company_requests.count_all(user_id=user_id)
            requests = await uow.company_requests.find_all(
                user_id=user_id, skip=skip, limit=limit
            )
            total_pages = (total_requests + limit - 1) // limit
            current_page = (skip // limit) + 1

            base_url = request_url.split("?")[0]
            previous_page_url = (
                f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"
                if current_page > 1
                else None
            )
            next_page_url = (
                f"{base_url}?skip={skip + limit}&limit={limit}"
                if current_page < total_pages
                else None
            )

            return CompanyRequestListResponse(
                total_pages=total_pages,
                current_page=current_page,
                requests=[
                    CompanyRequestResponse.model_validate(request)
                    for request in requests
                ],
                pagination=PaginationLinks(
                    previous=previous_page_url, next=next_page_url
                ),
            )
