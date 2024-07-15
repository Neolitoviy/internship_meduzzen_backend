from fastapi import Depends
from app.models.user import User
from app.services.user import UserService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.unitofwork import IUnitOfWork, UnitOfWork

auth_token_schemas = HTTPBearer()


async def authenticate_and_get_user(
    token: HTTPAuthorizationCredentials = Depends(auth_token_schemas),
    uow: IUnitOfWork = Depends(UnitOfWork),
    user_service: UserService = Depends(UserService)
) -> User:
    user = await user_service.create_user_from_token(uow, token)
    return user
