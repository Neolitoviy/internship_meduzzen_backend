import pytest
from httpx import AsyncClient

from app.main import app
from app.utils.unitofwork import IUnitOfWork


async def test_remove_member(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {"name": "Test Company", "description": "Test Description", "owner_id": current_user.id})
    member = await uow.company_members.add_one({"company_id": company.id, "user_id": current_user.id})
    await uow.commit()

    response = await ac.delete(f"/company_members/{member.id}")
    assert response.status_code == 204


async def test_leave_company(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {"name": "Test Company", "description": "Test Description", "owner_id": current_user.id})
    member = await uow.company_members.add_one({"company_id": company.id, "user_id": current_user.id})
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
