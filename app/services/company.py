from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse, PaginationLinks
from app.utils.unitofwork import IUnitOfWork
from app.core.exceptions import CompanyNotFound, CompanyPermissionError


class CompanyService:
    @staticmethod
    async def create_company(uow: IUnitOfWork, company: CompanyCreate, user_id: int) -> CompanyResponse:
        company_dict = company.model_dump()
        company_dict['owner_id'] = user_id
        async with uow:
            new_company = await uow.companies.add_one(company_dict)
            return CompanyResponse.model_validate(new_company)

    @staticmethod
    async def get_companies(uow: IUnitOfWork, skip: int, limit: int, request_url: str,
                            current_user_id: int) -> CompanyListResponse:
        async with uow:
            total_companies = await uow.companies.count_all()
            companies = await uow.companies.find_all(skip=skip, limit=limit)
            visible_companies = [
                company for company in companies if company.owner_id == current_user_id or company.visibility
            ]
            total_pages = (total_companies + limit - 1) // limit
            current_page = (skip // limit) + 1

            base_url = request_url.split('?')[0]
            previous_page_url = f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}" if current_page > 1 else None
            next_page_url = f"{base_url}?skip={skip + limit}&limit={limit}" if current_page < total_pages else None

            return CompanyListResponse(
                total_pages=total_pages,
                current_page=current_page,
                companies=[CompanyResponse.model_validate(company) for company in visible_companies],
                pagination=PaginationLinks(
                    previous=previous_page_url,
                    next=next_page_url
                )
            )

    @staticmethod
    async def get_company_by_id(uow: IUnitOfWork, company_id: int, current_user_id: int) -> CompanyResponse:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if not company or (company.owner_id != current_user_id and not company.visibility):
                raise CompanyNotFound(f"Company with id {company_id} not found")
            return CompanyResponse.model_validate(company)

    async def update_company(self, uow: IUnitOfWork, company_id: int, company: CompanyUpdate,
                             current_user_id: int) -> CompanyResponse:
        await self.check_company_owner(uow, company_id, current_user_id)
        company_dict = company.model_dump(exclude_unset=True)
        async with uow:
            updated_company = await uow.companies.edit_one(company_id, company_dict)
            if not updated_company:
                raise CompanyNotFound(f"Company with id {company_id} not found")
            return CompanyResponse.model_validate(updated_company)

    async def delete_company(self, uow: IUnitOfWork, company_id: int, current_user_id: int) -> CompanyResponse:
        await self.check_company_owner(uow, company_id, current_user_id)
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if not company:
                raise CompanyNotFound(f"Company with id {company_id} not found")
            await uow.companies.delete_one(company_id)
            return CompanyResponse.model_validate(company)

    @staticmethod
    async def check_company_owner(uow: IUnitOfWork, company_id: int, current_user_id: int) -> None:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if not company or company.owner_id != current_user_id:
                raise CompanyPermissionError(f"You don't have permission to modify this company")
