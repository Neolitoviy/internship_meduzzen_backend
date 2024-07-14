from fastapi import APIRouter, Request
from app.routers.dependencies import UOWDep, CurrentUserDep, CompanyMemberServiceDep
from app.schemas.company_member import CompanyMemberListResponse

router = APIRouter(
    prefix="/company_members",
    tags=["Company Members"],
)


@router.delete("/{member_id}", status_code=204)
async def remove_member(member_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyMemberServiceDep):
    return await service.remove_member(uow, member_id, current_user.id)


@router.post("/{company_id}/leave", status_code=204)
async def leave_company(company_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyMemberServiceDep):
    return await service.leave_company(uow, company_id, current_user.id)


@router.get("/", response_model=CompanyMemberListResponse)
async def get_memberships_by_company_id(
        request: Request,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: CompanyMemberServiceDep,
        company_id: int,
        skip: int = 0,
        limit: int = 10
):
    return await service.get_memberships(uow, current_user.id, company_id, skip, limit, str(request.url))


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
