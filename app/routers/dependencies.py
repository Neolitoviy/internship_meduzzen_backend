from typing import Annotated

from fastapi import Depends

from app.services.auth import authenticate_and_get_user
from app.services.company import CompanyService
from app.services.company_invitation import CompanyInvitationService
from app.services.company_member import CompanyMemberService
from app.services.company_request import CompanyRequestService
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork


def get_uow() -> IUnitOfWork:
    return UnitOfWork()


def get_users_service() -> UserService:
    return UserService()


def get_company_service() -> CompanyService:
    return CompanyService()


def get_company_invitation_service() -> CompanyInvitationService:
    return CompanyInvitationService()


def get_company_member_service() -> CompanyMemberService:
    return CompanyMemberService()


def get_company_request_service() -> CompanyRequestService:
    return CompanyRequestService()


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]
UserServiceDep = Annotated[UserService, Depends(get_users_service)]
CurrentUserDep = Annotated[UserService, Depends(authenticate_and_get_user)]
CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]
CompanyInvitationServiceDep = Annotated[
    CompanyInvitationService, Depends(get_company_invitation_service)
]
CompanyMemberServiceDep = Annotated[
    CompanyMemberService, Depends(get_company_member_service)
]
CompanyRequestServiceDep = Annotated[
    CompanyRequestService, Depends(get_company_request_service)
]
