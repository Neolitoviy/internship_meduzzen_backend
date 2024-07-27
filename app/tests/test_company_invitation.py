from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from faker import Faker

from app.core.exceptions import CompanyPermissionError
from app.schemas.company import CompanyResponse
from app.schemas.company_invitation import (
    CompanyInvitationCreate,
    CompanyInvitationResponse,
)
from app.schemas.user import UserInDB
from app.services.company_invitation import CompanyInvitationService

faker = Faker()


@pytest.fixture
def mock_invitation():
    return CompanyInvitationResponse(
        id=1,
        company_id=1,
        invited_user_id=2,
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
        hashed_password=faker.password(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_company():
    return CompanyResponse(
        id=1,
        name="Test Company",
        description="This is a test company.",
        visibility=True,
        owner_id=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_send_invitation(uow, mock_invitation, mock_user, mock_company):
    invitation_create = CompanyInvitationCreate(
        company_id=1,
        invited_user_id=2,
    )

    uow.companies.find_one.return_value = mock_company
    uow.company_invitations.add_one.return_value = mock_invitation

    invitation_response = await CompanyInvitationService.send_invitation(
        uow, invitation_create, mock_user.id
    )

    assert invitation_response.company_id == invitation_create.company_id
    assert invitation_response.invited_user_id == invitation_create.invited_user_id
    assert invitation_response.status == "pending"
    assert uow.company_invitations.add_one.called


@pytest.mark.asyncio
async def test_cancel_invitation(uow, mock_invitation, mock_user, mock_company):
    uow.companies.find_one.return_value = mock_company
    uow.company_invitations.find_one.return_value = mock_invitation

    await CompanyInvitationService.cancel_invitation(
        uow, mock_invitation.id, mock_user.id
    )

    assert uow.company_invitations.find_one.called
    assert uow.company_invitations.delete_one.called


@pytest.mark.asyncio
async def test_accept_invitation(uow, mock_invitation, mock_user):
    uow.company_invitations.find_one.return_value = mock_invitation
    uow.company_members.find_one.return_value = None
    uow.company_members.add_one.return_value = AsyncMock()

    await CompanyInvitationService.accept_invitation(
        uow, mock_invitation.id, mock_invitation.invited_user_id
    )

    assert uow.company_invitations.find_one.called
    assert uow.company_members.add_one.called


@pytest.mark.asyncio
async def test_decline_invitation(uow, mock_invitation, mock_user):
    uow.company_invitations.find_one.return_value = mock_invitation

    declined_invitation = await CompanyInvitationService.decline_invitation(
        uow, mock_invitation.id, mock_invitation.invited_user_id
    )

    assert uow.company_invitations.find_one.called
    assert declined_invitation.status == "declined"


@pytest.mark.asyncio
async def test_get_invitations(uow, mock_invitation):
    user_id = 1
    skip = 0
    limit = 10
    request_url = "http://testserver/company/invitations"

    uow.company_invitations.count_all.return_value = 1
    uow.company_invitations.find_all.return_value = [mock_invitation]

    invitations_response = await CompanyInvitationService.get_invitations(
        uow, user_id, skip, limit, request_url
    )

    assert invitations_response.total_pages == 1
    assert invitations_response.current_page == 1
    assert len(invitations_response.items) == 1
    assert invitations_response.items[0].company_id == mock_invitation.company_id
    assert (
        invitations_response.items[0].invited_user_id == mock_invitation.invited_user_id
    )


@pytest.mark.asyncio
async def test_check_not_self_invitation():
    with pytest.raises(CompanyPermissionError):
        await CompanyInvitationService.check_not_self_invitation(1, 1)


@pytest.mark.asyncio
async def test_check_already_member(uow, mock_user):
    uow.company_members.find_one.return_value = mock_user

    with pytest.raises(CompanyPermissionError):
        await CompanyInvitationService.check_already_member(uow, 1, mock_user.id)
