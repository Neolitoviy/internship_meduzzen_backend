from fastapi import APIRouter, Request
from app.routers.dependencies import UOWDep, CurrentUserDep, CompanyServiceDep
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse
import logging
from app.core.logging_config import logging_config

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.post("/", response_model=CompanyResponse)
async def create_company(company: CompanyCreate, uow: UOWDep, current_user: CurrentUserDep,
                         company_service: CompanyServiceDep):
    return await company_service.create_company(uow, company, current_user.id)


@router.get("/", response_model=CompanyListResponse)
async def get_companies(request: Request, uow: UOWDep, current_user: CurrentUserDep, company_service: CompanyServiceDep,
                        skip: int = 0, limit: int = 10):
    return await company_service.get_companies(uow, skip, limit, str(request.url), current_user.id)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, uow: UOWDep, current_user: CurrentUserDep, company_service: CompanyServiceDep):
    return await company_service.get_company_by_id(uow, company_id, current_user.id)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: int, company: CompanyUpdate, uow: UOWDep, current_user: CurrentUserDep,
                         company_service: CompanyServiceDep):
    return await company_service.update_company(uow, company_id, company, current_user.id)


@router.delete("/{company_id}", response_model=CompanyResponse)
async def delete_company(company_id: int, uow: UOWDep, current_user: CurrentUserDep,
                         company_service: CompanyServiceDep):
    return await company_service.delete_company(uow, company_id, current_user.id)
