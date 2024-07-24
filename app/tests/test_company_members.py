from httpx import AsyncClient

from app.schemas.company import CompanyCreate
from app.services.company import CompanyService
from app.services.company_invitation import CompanyInvitationService
from app.services.company_member import CompanyMemberService
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork


async def test_remove_member(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {
            "name": "Test Company",
            "description": "Test Description",
            "owner_id": current_user.id,
        }
    )
    member = await uow.company_members.add_one(
        {"company_id": company.id, "user_id": current_user.id}
    )
    await uow.commit()

    response = await ac.delete(f"/company_members/{member.id}")
    assert response.status_code == 204


async def test_leave_company(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {
            "name": "Test Company",
            "description": "Test Description",
            "owner_id": current_user.id,
        }
    )
    member = await uow.company_members.add_one(
        {"company_id": company.id, "user_id": current_user.id}
    )
    await uow.commit()

    response = await ac.post(f"/company_members/{company.id}/leave")
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == company.id
    assert data["user_id"] == current_user.id


async def test_get_memberships(ac: AsyncClient, uow: IUnitOfWork, current_user):
    response = await ac.get("/company_members/")
    assert response.status_code == 200
    data = response.json()
    assert "memberships" in data
    assert isinstance(data["memberships"], list)


async def test_appoint_admin(
    ac: AsyncClient,
    uow: IUnitOfWork,
    user_service: UserService,
    company_service: CompanyService,
    member_service: CompanyMemberService,
    invitation_service: CompanyInvitationService,
    create_test_user,
):
    # Create the company owner and get the token
    owner, owner_token = await create_test_user(email="owner@example.com")

    # Create the company
    company_create = CompanyCreate(
        name="Test Company", description="A test company", visibility=True
    )
    company = await company_service.create_company(uow, company_create, owner.id)

    # Create another user and get the token
    member, member_token = await create_test_user(email="member@example.com")

    # Send invitation to the user to join the company
    await invitation_service.send_invitation(uow, company.id, member.email, owner.id)

    # Accept the invitation as the user
    invitation = await uow.company_invitations.find_one(
        company_id=company.id, invited_user_id=member.id
    )
    await invitation_service.accept_invitation(uow, invitation.id, member.id)

    # Appoint the user as an administrator
    response = await ac.post(
        f"/company_members/{company.id}/admin/{member.id}/appoint",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 204

    # Check that the user is now an administrator
    async with uow:
        updated_member = await uow.company_members.find_one(
            company_id=company.id, user_id=member.id
        )
    assert updated_member.is_admin is True


async def test_remove_admin(
    ac: AsyncClient,
    uow: IUnitOfWork,
    user_service: UserService,
    company_service: CompanyService,
    member_service: CompanyMemberService,
    invitation_service: CompanyInvitationService,
    create_test_user,
):
    # Create the company owner and get the token
    owner, owner_token = await create_test_user

    # Create the company
    company_create = CompanyCreate(
        name="Test Company", description="A test company", visibility=True
    )
    company = await company_service.create_company(uow, company_create, owner.id)

    # Create another user and get the token
    member, member_token = await create_test_user

    # Send invitation to the user to join the company
    await invitation_service.send_invitation(uow, company.id, member.email, owner.id)

    # Accept the invitation as the user
    invitation = await uow.company_invitations.find_one(
        company_id=company.id, invited_user_id=member.id
    )
    await invitation_service.accept_invitation(uow, invitation.id, member.id)

    # Appoint the user as an administrator
    async with uow:
        await uow.company_members.edit_one(member.id, {"is_admin": True})

    # Remove the user as an administrator
    response = await ac.post(
        f"/company_members/{company.id}/admin/{member.id}/remove",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 204

    # Check that the user is no longer an administrator
    async with uow:
        updated_member = await uow.company_members.find_one(
            company_id=company.id, user_id=member.id
        )
    assert updated_member.is_admin is False
