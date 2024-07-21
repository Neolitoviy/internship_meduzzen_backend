from app.schemas.company_member import CompanyMemberListResponse, CompanyMemberResponse, PaginationLinks
from app.utils.unitofwork import IUnitOfWork
from app.core.exceptions import CompanyPermissionError, MemberNotFound


class CompanyMemberService:
    @staticmethod
    async def remove_member(uow: IUnitOfWork, member_id: int, current_user_id: int) -> None:
        async with uow:
            member = await uow.company_members.find_one(id=member_id)
            if not member:
                raise MemberNotFound("Member not found")
            company = await uow.companies.find_one(id=member.company_id)
            if company and company.owner_id == current_user_id:
                await uow.company_members.delete_one(member_id)
                return
        raise CompanyPermissionError("You don't have permission to remove this member")

    @staticmethod
    async def leave_company(uow: IUnitOfWork, company_id: int, current_user_id: int) -> None:
        async with uow:
            member = await uow.company_members.find_one(user_id=current_user_id, company_id=company_id)
            if member:
                await uow.company_members.delete_one(member.id)
                return
        raise MemberNotFound("You are not a member of this company")

    @staticmethod
    async def get_memberships(uow: IUnitOfWork, user_id: int, company_id: int, skip: int, limit: int, request_url: str) -> CompanyMemberListResponse:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if not company or company.owner_id != user_id:
                raise CompanyPermissionError("You don't have permission to view this company's members.")

            total_members = await uow.company_members.count_all(company_id=company_id)
            members = await uow.company_members.find_all(skip=skip, limit=limit, company_id=company_id)
            total_pages = (total_members + limit - 1) // limit
            current_page = (skip // limit) + 1

            base_url = request_url.split('?')[0]
            previous_page_url = f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}" if current_page > 1 else None
            next_page_url = f"{base_url}?skip={skip + limit}&limit={limit}" if current_page < total_pages else None

            return CompanyMemberListResponse(
                current_page=current_page,
                total_pages=total_pages,
                members=[CompanyMemberResponse.model_validate(member) for member in members],
                pagination=PaginationLinks(
                    previous=previous_page_url,
                    next=next_page_url
                )
            )