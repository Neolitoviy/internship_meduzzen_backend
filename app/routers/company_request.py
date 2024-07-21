from fastapi import APIRouter, Request
from app.schemas.company_request import CompanyRequestCreate, CompanyRequestResponse, CompanyRequestListResponse
from app.routers.dependencies import UOWDep, CurrentUserDep, CompanyRequestServiceDep

router = APIRouter(
    prefix="/request",
    tags=["Request"],
)


@router.delete("/{request_id}/cancel", status_code=204)
async def cancel_request(request_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyRequestServiceDep):
    return await service.cancel_request(uow, request_id, current_user.id)


@router.post("/{request_id}/accept", status_code=204)
async def accept_request(request_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyRequestServiceDep):
    return await service.accept_request(uow, request_id, current_user.id)


@router.post("/{request_id}/decline", status_code=204)
async def decline_request(request_id: int, uow: UOWDep, current_user: CurrentUserDep,
                          service: CompanyRequestServiceDep):
    return await service.decline_request(uow, request_id, current_user.id)
