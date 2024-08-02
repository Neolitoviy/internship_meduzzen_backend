from datetime import datetime
from unittest.mock import patch

import pytest
from faker import Faker

from app.schemas.company import CompanyResponse
from app.schemas.company_member import CompanyMemberResponse
from app.services.company import CompanyService
from app.services.company_member import CompanyMemberService

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


@pytest.fixture
def mock_member():
    return CompanyMemberResponse(
        id=1, company_id=1, user_id=1, is_admin=False, created_at=datetime.utcnow()
    )


@pytest.mark.asyncio
async def test_remove_member(uow, mock_member):
    member_id = mock_member.id
    current_user_id = 1

    uow.company_members.find_one.return_value = mock_member
    uow.company_members.delete_one.return_value = None

    with patch.object(CompanyService, "check_company_owner", return_value=None):
        await CompanyMemberService.remove_member(uow, member_id, current_user_id)

    assert uow.company_members.find_one.called
    assert uow.company_members.delete_one.called


@pytest.mark.asyncio
async def test_leave_company(uow, mock_member):
    company_id = mock_member.company_id
    current_user_id = mock_member.user_id

    uow.company_members.find_one.return_value = mock_member
    uow.company_members.delete_one.return_value = None

    await CompanyMemberService.leave_company(uow, company_id, current_user_id)

    assert uow.company_members.find_one.called
    assert uow.company_members.delete_one.called


@pytest.mark.asyncio
async def test_get_memberships(uow, mock_member):
    company_id = mock_member.company_id
    user_id = mock_member.user_id
    skip = 0
    limit = 10
    request_url = "http://testserver/company/1/members"
    is_admin = None

    uow.company_members.count_all.return_value = 1
    uow.company_members.find_all.return_value = [mock_member]

    with patch.object(CompanyService, "check_company_permission", return_value=None):
        response = await CompanyMemberService.get_memberships(
            uow, user_id, company_id, skip, limit, request_url, is_admin
        )

    assert response.current_page == 1
    assert response.total_pages == 1
    assert len(response.items) == 1
    assert response.items[0].id == mock_member.id


@pytest.mark.asyncio
async def test_appoint_admin(uow, mock_member):
    company_id = mock_member.company_id
    user_id = mock_member.user_id
    current_user_id = 1

    uow.company_members.find_one.return_value = mock_member

    with patch.object(CompanyService, "check_company_owner", return_value=None):
        await CompanyMemberService.appoint_admin(
            uow, company_id, user_id, current_user_id
        )

    assert uow.company_members.find_one.called
    assert mock_member.is_admin == True


@pytest.mark.asyncio
async def test_remove_admin(uow, mock_member):
    company_id = mock_member.company_id
    user_id = mock_member.user_id
    current_user_id = 1

    uow.company_members.find_one.return_value = mock_member

    with patch.object(CompanyService, "check_company_owner", return_value=None):
        await CompanyMemberService.remove_admin(
            uow, company_id, user_id, current_user_id
        )

    assert uow.company_members.find_one.called
    assert mock_member.is_admin == False
