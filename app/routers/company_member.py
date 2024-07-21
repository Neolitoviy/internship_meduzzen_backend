from fastapi import APIRouter, Request
from app.routers.dependencies import UOWDep, CurrentUserDep, CompanyMemberServiceDep
from app.schemas.company_member import CompanyMemberListResponse

router = APIRouter(
    prefix="/member",
    tags=["Member"],
)


@router.delete("/{member_id}", status_code=204)
async def remove_member(member_id: int, uow: UOWDep, current_user: CurrentUserDep, service: CompanyMemberServiceDep):
    return await service.remove_member(uow, member_id, current_user.id)