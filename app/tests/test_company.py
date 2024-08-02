from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from faker import Faker

from app.core.exceptions import CompanyPermissionError
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.company import CompanyService

faker = Faker()


@pytest.fixture
def mock_company():
    return CompanyResponse(
        id=1,
        name=faker.company(),
        description=faker.text(),
        visibility=True,
        owner_id=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_create_company(uow, mock_company):
    company_create = CompanyCreate(
        name=mock_company.name,
        description=mock_company.description,
        visibility=mock_company.visibility,
    )
    user_id = 1

    uow.companies.add_one.return_value = mock_company
    uow.company_members.add_one.return_value = AsyncMock()

    company_response = await CompanyService.create_company(uow, company_create, user_id)

    assert company_response.name == company_create.name
    assert company_response.description == company_create.description
    assert company_response.visibility == company_create.visibility
    assert uow.companies.add_one.called
    assert uow.company_members.add_one.called


@pytest.mark.asyncio
async def test_get_companies(uow, mock_company):
    skip = 0
    limit = 10
    request_url = "http://testserver/api/companies"
    current_user_id = 1

    total_companies = 1
    companies = [mock_company]

    uow.companies.count_visible_companies.return_value = total_companies
    uow.companies.find_visible_companies.return_value = companies

    company_list_response = await CompanyService.get_companies(
        uow, skip, limit, request_url, current_user_id
    )

    assert company_list_response.total_pages == 1
    assert company_list_response.current_page == 1
    assert len(company_list_response.items) == 1
    assert company_list_response.items[0].name == mock_company.name
    assert uow.companies.count_visible_companies.called
    assert uow.companies.find_visible_companies.called


@pytest.mark.asyncio
async def test_get_company_by_id(uow, mock_company):
    company_id = 1
    current_user_id = 1

    uow.companies.find_one.return_value = mock_company

    company_response = await CompanyService.get_company_by_id(
        uow, company_id, current_user_id
    )

    assert company_response.name == mock_company.name
    assert company_response.description == mock_company.description
    assert uow.companies.find_one.called


@pytest.mark.asyncio
async def test_update_company(uow, mock_company):
    company_id = 1
    user_id = 1
    company_update = CompanyUpdate(
        name="Updated Company", description="Updated Description"
    )

    uow.companies.find_one.return_value = mock_company
    uow.companies.edit_one.return_value = mock_company

    company_service = CompanyService()
    updated_company_response = await company_service.update_company(
        uow, company_id, company_update, user_id
    )

    assert updated_company_response.name == mock_company.name
    assert updated_company_response.description == mock_company.description
    assert uow.companies.edit_one.called


@pytest.mark.asyncio
async def test_delete_company(uow, mock_company):
    company_id = 1
    user_id = 1

    company_service = CompanyService()

    uow.companies.find_one.return_value = mock_company

    await company_service.delete_company(uow, company_id, user_id)

    assert uow.companies.delete_one.called


@pytest.mark.asyncio
async def test_check_company_owner(uow, mock_company):
    company_id = 1
    user_id = 1

    uow.companies.find_one.return_value = mock_company

    await CompanyService.check_company_owner(uow, company_id, user_id)

    assert uow.companies.find_one.called

    uow.companies.find_one.return_value.owner_id = 2

    with pytest.raises(CompanyPermissionError):
        await CompanyService.check_company_owner(uow, company_id, user_id)


@pytest.mark.asyncio
async def test_check_company_permission(uow, mock_company):
    company_id = 1
    user_id = 1
    is_admin = True

    uow.company_members.find_one_or_none.return_value = AsyncMock()

    await CompanyService.check_company_permission(uow, company_id, user_id, is_admin)

    assert uow.company_members.find_one_or_none.called

    uow.company_members.find_one_or_none.return_value = None

    with pytest.raises(CompanyPermissionError):
        await CompanyService.check_company_permission(
            uow, company_id, user_id, is_admin
        )
