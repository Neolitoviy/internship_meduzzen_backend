from fastapi import APIRouter, Request
from app.routers.dependencies import UOWDep, CurrentUserDep, CompanyServiceDep, CompanyRequestServiceDep, \
    CompanyInvitationServiceDep, CompanyMemberServiceDep
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse
from app.schemas.company_invitation import CompanyInvitationResponse, CompanyInvitationCreate
from app.schemas.company_member import CompanyMemberListResponse
from app.schemas.company_request import CompanyRequestCreate, CompanyRequestResponse
import logging
from app.core.logging_config import logging_config

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/company",
    tags=["Company"],
)


@router.post("/", response_model=CompanyResponse)
async def create_company(company: CompanyCreate, uow: UOWDep, current_user: CurrentUserDep,
                         company_service: CompanyServiceDep):
    return await company_service.create_company(uow, company, current_user.id)


@router.get("/", response_model=CompanyListResponse)
async def get_companies(request: Request, uow: UOWDep, current_user: CurrentUserDep, company_service: CompanyServiceDep,
                        skip: int = 0, limit: int = 10):
    return await company_service.get_companies(uow, skip, limit, str(request.url), current_user.id)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, uow: UOWDep, current_user: CurrentUserDep, company_service: CompanyServiceDep):
    return await company_service.get_company_by_id(uow, company_id, current_user.id)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: int, company: CompanyUpdate, uow: UOWDep, current_user: CurrentUserDep,
                         company_service: CompanyServiceDep):
    return await company_service.update_company(uow, company_id, company, current_user.id)


@router.delete("/{company_id}", response_model=CompanyResponse)
async def delete_company(company_id: int, uow: UOWDep, current_user: CurrentUserDep,
                         company_service: CompanyServiceDep):
    return await company_service.delete_company(uow, company_id, current_user.id)


@router.post("/{company_id}/join", response_model=CompanyRequestResponse)
async def request_to_join_company(company_id: int, uow: UOWDep, current_user: CurrentUserDep,
                                  service: CompanyRequestServiceDep):
    request = CompanyRequestCreate(company_id=company_id)
    return await service.request_to_join_company(uow, request, current_user.id)


@router.post("/{company_id}/invite/{user_id}", response_model=CompanyInvitationResponse)
async def invite_user_to_company(company_id: int, user_id: int, uow: UOWDep, current_user: CurrentUserDep,
                                 service: CompanyInvitationServiceDep):
    invitation = CompanyInvitationCreate(company_id=company_id, invited_user_id=user_id)
    return await service.send_invitation(uow, invitation, current_user.id)


@router.post("/{company_id}/leave", status_code=204)
async def leave_company(company_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyMemberServiceDep):
    return await service.leave_company(uow, company_id, current_user.id)


@router.get("/{company_id}/members", response_model=CompanyMemberListResponse)
async def get_memberships_by_company_id(request: Request, uow: UOWDep, current_user: CurrentUserDep,
                                        service: CompanyMemberServiceDep, company_id: int, skip: int = 0,
                                        limit: int = 10):
    return await service.get_memberships(uow, current_user.id, company_id, skip, limit, str(request.url))


@router.delete("/members/{member_id}", status_code=204)
async def remove_member(member_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyMemberServiceDep):
    return await service.remove_member(uow, member_id, current_user.id)


@router.post("/{company_id}/admin/{user_id}/appoint", status_code=204)
async def appoint_admin(
        company_id: int,
        user_id: int,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: CompanyMemberServiceDep
):
    return await service.appoint_admin(uow, company_id, user_id, current_user.id)


@router.post("/{company_id}/admin/{user_id}/remove", status_code=204)
async def remove_admin(
        company_id: int,
        user_id: int,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: CompanyMemberServiceDep
):
    return await service.remove_admin(uow, company_id, user_id, current_user.id)


@router.get("/{company_id}/admins", response_model=CompanyMemberListResponse)
async def get_admins(
        request: Request,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: CompanyMemberServiceDep,
        company_id: int,
        skip: int = 0,
        limit: int = 10,
):
    return await service.get_memberships(uow, current_user.id, company_id, skip, limit, str(request.url), is_admin=True)
