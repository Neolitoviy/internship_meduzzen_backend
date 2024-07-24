from httpx import AsyncClient

from app.schemas.company_request import CompanyRequestCreate
from app.utils.unitofwork import IUnitOfWork


async def test_request_to_join_company(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {
            "name": "Test Company",
            "description": "Test Description",
            "owner_id": current_user.id,
        }
    )
    await uow.commit()

    request_data = CompanyRequestCreate(company_id=company.id)
    response = await ac.post("/company_requests/", json=request_data.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == request_data.company_id
    assert data["requested_user_id"] == current_user.id


async def test_get_requests(ac: AsyncClient, uow: IUnitOfWork, current_user):
    response = await ac.get("/company_requests/")
    assert response.status_code == 200
    data = response.json()
    assert "requests" in data
    assert isinstance(data["requests"], list)


async def test_cancel_request(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {
            "name": "Test Company",
            "description": "Test Description",
            "owner_id": current_user.id,
        }
    )
    request = await uow.company_requests.add_one(
        {"company_id": company.id, "requested_user_id": current_user.id}
    )
    await uow.commit()

    response = await ac.delete(f"/company_requests/{request.id}")
    assert response.status_code == 204


async def test_accept_request(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {
            "name": "Test Company",
            "description": "Test Description",
            "owner_id": current_user.id,
        }
    )
    request = await uow.company_requests.add_one(
        {"company_id": company.id, "requested_user_id": current_user.id}
    )
    await uow.commit()

    response = await ac.post(f"/company_requests/{request.id}/accept")
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == company.id
    assert data["requested_user_id"] == current_user.id


async def test_decline_request(ac: AsyncClient, uow: IUnitOfWork, current_user):
    company = await uow.companies.add_one(
        {
            "name": "Test Company",
            "description": "Test Description",
            "owner_id": current_user.id,
        }
    )
    request = await uow.company_requests.add_one(
        {"company_id": company.id, "requested_user_id": current_user.id}
    )
    await uow.commit()

    response = await ac.post(f"/company_requests/{request.id}/decline")
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == company.id
    assert data["requested_user_id"] == current_user.id
