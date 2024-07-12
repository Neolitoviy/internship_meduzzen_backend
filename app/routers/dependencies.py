from typing import Annotated
from fastapi import Depends

from app.services.auth import authenticate_and_get_user
from app.services.company import CompanyService
from app.utils.unitofwork import UnitOfWork, IUnitOfWork
from app.services.user import UserService


def get_uow() -> IUnitOfWork:
    return UnitOfWork()


def get_users_service() -> UserService:
    return UserService()


def get_company_service() -> CompanyService:
    return CompanyService()


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]
UserServiceDep = Annotated[UserService, Depends(get_users_service)]
CurrentUserDep = Annotated[UserService, Depends(authenticate_and_get_user)]
CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]
