from app.schemas.company_request import CompanyRequestCreate, CompanyRequestResponse, CompanyRequestListResponse, \
    PaginationLinks
from app.utils.unitofwork import IUnitOfWork
from app.core.exceptions import CompanyPermissionError, RequestNotFound


class CompanyRequestService:
    @staticmethod
    async def request_to_join_company(uow: IUnitOfWork, request: CompanyRequestCreate,
                                      current_user_id: int) -> CompanyRequestResponse:
        request_dict = request.dict()
        request_dict['requested_user_id'] = current_user_id
        async with uow:
            new_request = await uow.company_requests.add_one(request_dict)
            return CompanyRequestResponse.model_validate(new_request)

    @staticmethod
    async def cancel_request(uow: IUnitOfWork, request_id: int, current_user_id: int) -> None:
        async with uow:
            request = await uow.company_requests.find_one(id=request_id)
            if not request or request.requested_user_id != current_user_id:
                raise CompanyPermissionError("You don't have permission to cancel this request")
            await uow.company_requests.delete_one(request_id)

    @staticmethod
    async def accept_request(uow: IUnitOfWork, request_id: int, current_user_id: int) -> None:
        async with uow:
            request = await uow.company_requests.find_one(id=request_id)
            if not request:
                raise RequestNotFound("Request not found")
            company = await uow.companies.find_one(id=request.company_id)
            if company.owner_id != current_user_id:
                raise CompanyPermissionError("You don't have permission to accept this request")
            await uow.company_members.add_one({"user_id": request.requested_user_id, "company_id": request.company_id})
            request.status = 'accepted'

    @staticmethod
    async def decline_request(uow: IUnitOfWork, request_id: int, current_user_id: int) -> None:
        async with uow:
            request = await uow.company_requests.find_one(id=request_id)
            if not request:
                raise RequestNotFound("Request not found")
            company = await uow.companies.find_one(id=request.company_id)
            if company.owner_id != current_user_id:
                raise CompanyPermissionError("You don't have permission to decline this request")
            request.status = 'declined'

    @staticmethod
    async def get_requests_by_user_id(uow: IUnitOfWork, user_id: int, skip: int, limit: int,
                                      request_url: str) -> CompanyRequestListResponse:
        async with uow:
            total_requests = await uow.company_requests.count_all(user_id=user_id)
            requests = await uow.company_requests.find_all(user_id=user_id, skip=skip, limit=limit)
            total_pages = (total_requests + limit - 1) // limit
            current_page = (skip // limit) + 1

            base_url = request_url.split('?')[0]
            previous_page_url = f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}" if current_page > 1 else None
            next_page_url = f"{base_url}?skip={skip + limit}&limit={limit}" if current_page < total_pages else None

            return CompanyRequestListResponse(
                total_pages=total_pages,
                current_page=current_page,
                requests=[CompanyRequestResponse.model_validate(request) for request in requests],
                pagination=PaginationLinks(
                    previous=previous_page_url,
                    next=next_page_url
                )
            )
