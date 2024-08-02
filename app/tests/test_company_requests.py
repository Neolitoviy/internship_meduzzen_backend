from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from faker import Faker

from app.schemas.company_request import CompanyRequestCreate, CompanyRequestResponse
from app.schemas.user import UserInDB
from app.services.company_request import CompanyRequestService

faker = Faker()


@pytest.fixture
def mock_request():
    return CompanyRequestResponse(
        id=1,
        company_id=1,
        requested_user_id=1,
        status="pending",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_user():
    return UserInDB(
        id=1,
        email=faker.email(),
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        is_active=True,
        hashed_password="hashed_password",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_request_to_join_company(uow, mock_request, mock_user):
    request_create = CompanyRequestCreate(company_id=1)

    uow.company_requests.add_one.return_value = mock_request

    request_response = await CompanyRequestService.request_to_join_company(
        uow, request_create, mock_user.id
    )

    assert request_response.company_id == request_create.company_id
    assert request_response.requested_user_id == mock_user.id
    assert request_response.status == "pending"
    assert uow.company_requests.add_one.called


@pytest.mark.asyncio
async def test_cancel_request(uow, mock_request, mock_user):
    uow.company_requests.find_one.return_value = mock_request

    with patch(
        "app.services.user.UserService.check_user_permission", return_value=None
    ):
        await CompanyRequestService.cancel_request(uow, mock_request.id, mock_user.id)

    assert uow.company_requests.delete_one.called


@pytest.mark.asyncio
async def test_accept_request(uow, mock_request, mock_user):
    uow.company_requests.find_one.return_value = mock_request
    uow.company_members.add_one.return_value = AsyncMock()

    with patch(
        "app.services.company.CompanyService.check_company_owner", return_value=None
    ):
        with patch(
            "app.services.company_invitation.CompanyInvitationService.check_already_member",
            return_value=None,
        ):
            new_membership = await CompanyRequestService.accept_request(
                uow, mock_request.id, mock_user.id
            )

    assert new_membership is not None
    assert uow.company_members.add_one.called


@pytest.mark.asyncio
async def test_decline_request(uow, mock_request, mock_user):
    uow.company_requests.find_one.return_value = mock_request

    with patch(
        "app.services.company.CompanyService.check_company_owner", return_value=None
    ):
        declined_request = await CompanyRequestService.decline_request(
            uow, mock_request.id, mock_user.id
        )

    assert declined_request.status == "declined"
    assert uow.company_requests.find_one.called


@pytest.mark.asyncio
async def test_get_requests_by_user_id(uow, mock_request, mock_user):
    uow.company_requests.count_all.return_value = 1
    uow.company_requests.find_all.return_value = [mock_request]

    request_url = "http://testserver/company/requests"
    response = await CompanyRequestService.get_requests_by_user_id(
        uow, mock_user.id, 0, 10, request_url
    )

    assert response.total_pages == 1
    assert response.current_page == 1
    assert len(response.items) == 1
    assert response.items[0].id == mock_request.id
    assert uow.company_requests.find_all.called
    assert uow.company_requests.count_all.called
