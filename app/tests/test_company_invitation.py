import pytest
from httpx import AsyncClient

from app.main import app
from app.schemas.company_invitation import CompanyInvitationCreate
from app.utils.unitofwork import IUnitOfWork


async def test_send_invitation(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {"name": "Test Company", "description": "Test Description", "owner_id": current_user.id})
    await uow.commit()

    invitation_data = CompanyInvitationCreate(company_id=company.id, invited_user_id=current_user.id)
    response = await ac.post("/company_invitations/", json=invitation_data.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == invitation_data.company_id
    assert data["invited_user_id"] == invitation_data.invited_user_id


async def test_get_invitations(ac: AsyncClient, uow: IUnitOfWork, current_user):
    response = await ac.get("/company_invitations/")
    assert response.status_code == 200
    data = response.json()
    assert "invitations" in data
    assert isinstance(data["invitations"], list)


async def test_cancel_invitation(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {"name": "Test Company", "description": "Test Description", "owner_id": current_user.id})
    invitation = await uow.company_invitations.add_one(
        {"company_id": company.id, "invited_user_id": current_user.id, "invited_by": current_user.id})
    await uow.commit()

    response = await ac.delete(f"/company_invitations/{invitation.id}")
    assert response.status_code == 204


async def test_accept_invitation(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {"name": "Test Company", "description": "Test Description", "owner_id": current_user.id})
    invitation = await uow.company_invitations.add_one(
        {"company_id": company.id, "invited_user_id": current_user.id, "invited_by": current_user.id})
    await uow.commit()

    response = await ac.post(f"/company_invitations/{invitation.id}/accept")
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == company.id
    assert data["invited_user_id"] == current_user.id


async def test_decline_invitation(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {"name": "Test Company", "description": "Test Description", "owner_id": current_user.id})
    invitation = await uow.company_invitations.add_one(
        {"company_id": company.id, "invited_user_id": current_user.id, "invited_by": current_user.id})
    await uow.commit()

    response = await ac.post(f"/company_invitations/{invitation.id}/decline")
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == company.id
    assert data["invited_user_id"] == current_user.id
