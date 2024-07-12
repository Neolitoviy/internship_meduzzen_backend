import pytest
from httpx import AsyncClient

from app.core.exceptions import CompanyNotFound
from app.services.company import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.utils.unitofwork import IUnitOfWork


async def test_create_company(ac: AsyncClient, uow: IUnitOfWork, current_user_id: int):
    company_create = CompanyCreate(
        name="Test Company",
        description="A test company"
    )

    company_service = CompanyService()
    company = await company_service.create_company(uow, company_create, current_user_id)

    assert company.name == company_create.name
    assert company.description == company_create.description
    assert company.owner_id == current_user_id


async def test_update_company(ac: AsyncClient, uow: IUnitOfWork, current_user_id: int):
    company_service = CompanyService()

    company_create = CompanyCreate(
        name="Test Company",
        description="A test company"
    )
    created_company = await company_service.create_company(uow, company_create, current_user_id)

    company_update = CompanyUpdate(
        name="Updated Company",
        description="An updated test company"
    )
    updated_company = await company_service.update_company(uow, created_company.id, company_update, current_user_id)

    assert updated_company.name == company_update.name
    assert updated_company.description == company_update.description


async def test_delete_company(ac: AsyncClient, uow: IUnitOfWork, current_user_id: int):
    company_service = CompanyService()

    company_create = CompanyCreate(
        name="Test Company",
        description="A test company"
    )
    created_company = await company_service.create_company(uow, company_create, current_user_id)

    await company_service.delete_company(uow, created_company.id, current_user_id)

    with pytest.raises(CompanyNotFound):
        await company_service.get_company_by_id(uow, created_company.id)


async def test_get_companies(ac: AsyncClient, uow: IUnitOfWork, current_user_id: int):
    company_service = CompanyService()

    for i in range(15):
        company_create = CompanyCreate(
            name=f"Test Company {i}",
            description=f"A test company {i}"
        )
        await company_service.create_company(uow, company_create, current_user_id)

    companies_response = await company_service.get_companies(uow, skip=0, limit=10,
                                                             request_url="http://test.com/companies")
    assert len(companies_response.companies) == 10
    assert companies_response.total_pages > 1


async def test_get_company_by_id(ac: AsyncClient, uow: IUnitOfWork, current_user_id: int):
    company_service = CompanyService()

    company_create = CompanyCreate(
        name="Test Company",
        description="A test company"
    )
    created_company = await company_service.create_company(uow, company_create, current_user_id)

    retrieved_company = await company_service.get_company_by_id(uow, created_company.id)

    assert retrieved_company is not None
    assert retrieved_company.name == company_create.name
    assert retrieved_company.description == company_create.description
