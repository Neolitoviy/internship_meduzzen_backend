from fastapi import APIRouter, Request
from app.schemas.company_request import CompanyRequestCreate, CompanyRequestResponse, CompanyRequestListResponse
from app.routers.dependencies import UOWDep, CurrentUserDep, CompanyRequestServiceDep

router = APIRouter(
    prefix="/company_requests",
    tags=["Company Requests"],
)


@router.post("/", response_model=CompanyRequestResponse)
async def request_to_join_company(request: CompanyRequestCreate, uow: UOWDep, current_user: CurrentUserDep,
                                  service: CompanyRequestServiceDep):
    return await service.request_to_join_company(uow, request, current_user.id)


@router.delete("/{request_id}", status_code=204)
async def cancel_request(request_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyRequestServiceDep):
    return await service.cancel_request(uow, request_id, current_user.id)


@router.post("/{request_id}/accept", status_code=204)
async def accept_request(request_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyRequestServiceDep):
    return await service.accept_request(uow, request_id, current_user.id)


@router.post("/{request_id}/decline", status_code=204)
async def decline_request(request_id: int, uow: UOWDep, current_user: CurrentUserDep,
                          service: CompanyRequestServiceDep):
    return await service.decline_request(uow, request_id, current_user.id)


@router.get("/", response_model=CompanyRequestListResponse)
async def get_requests(
        request: Request,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: CompanyRequestServiceDep,
        skip: int = 0,
        limit: int = 10
):
    return await service.get_requests_by_user_id(uow, current_user.id, skip, limit, str(request.url))
