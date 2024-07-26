from app.core.exceptions import CompanyPermissionError
from app.schemas.company import (
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.utils.pagination import paginate
from app.utils.unitofwork import IUnitOfWork


class CompanyService:
    @staticmethod
    async def create_company(
        uow: IUnitOfWork, company: CompanyCreate, user_id: int
    ) -> CompanyResponse:
        company_dict = company.model_dump()
        company_dict["owner_id"] = user_id
        async with uow:
            new_company = await uow.companies.add_one(company_dict)
            company_member_dict = {
                "company_id": new_company.id,
                "user_id": user_id,
                "is_admin": True,  # Owner like admin
            }
            await uow.company_members.add_one(company_member_dict)
            return CompanyResponse.model_validate(new_company)

    @staticmethod
    async def get_companies(
        uow: IUnitOfWork,
        skip: int,
        limit: int,
        request_url: str,
        current_user_id: int,
    ) -> CompanyListResponse:
        async with uow:
            total_companies = await uow.companies.count_visible_companies(
                user_id=current_user_id
            )
            companies = await uow.companies.find_visible_companies(
                skip=skip, limit=limit, user_id=current_user_id
            )

            companies_response = [
                CompanyResponse.model_validate(company) for company in companies
            ]
            pagination_response = paginate(
                items=companies_response,
                total_items=total_companies,
                skip=skip,
                limit=limit,
                request_url=request_url,
            )

            return CompanyListResponse(
                total_pages=pagination_response.total_pages,
                current_page=pagination_response.current_page,
                items=pagination_response.items,
                pagination=pagination_response.pagination,
            )

    @staticmethod
    async def get_company_by_id(
        uow: IUnitOfWork, company_id: int, current_user_id: int
    ) -> CompanyResponse:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if company.owner_id == current_user_id or company.visibility:
                return CompanyResponse.model_validate(company)

    async def update_company(
        self,
        uow: IUnitOfWork,
        company_id: int,
        company: CompanyUpdate,
        current_user_id: int,
    ) -> CompanyResponse:
        await self.check_company_owner(uow, company_id, current_user_id)
        company_dict = company.model_dump(exclude_unset=True)
        async with uow:
            updated_company = await uow.companies.edit_one(company_id, company_dict)
            return CompanyResponse.model_validate(updated_company)

    async def delete_company(
        self, uow: IUnitOfWork, company_id: int, current_user_id: int
    ) -> None:
        await self.check_company_owner(uow, company_id, current_user_id)
        async with uow:
            await uow.companies.delete_one(company_id)

    @staticmethod
    async def check_company_owner(
        uow: IUnitOfWork, company_id: int, current_user_id: int
    ) -> None:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if company.owner_id != current_user_id:
                raise CompanyPermissionError(
                    "You don't have permission to this company"
                )

    @staticmethod
    async def check_company_permission(
        uow: IUnitOfWork, company_id: int, current_user_id: int, is_admin: bool = False
    ) -> None:
        filters = {"company_id": company_id, "user_id": current_user_id}
        if is_admin:
            filters["is_admin"] = True

        if not await uow.company_members.find_one_or_none(**filters):
            raise CompanyPermissionError(
                "You do not have permission to perform this action in this company."
            )
