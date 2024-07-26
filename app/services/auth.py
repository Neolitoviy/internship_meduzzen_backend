from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user import UserInDB
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

auth_token_schemas = HTTPBearer()


async def authenticate_and_get_user(
    token: HTTPAuthorizationCredentials = Depends(auth_token_schemas),
    uow: IUnitOfWork = Depends(UnitOfWork),
    user_service: UserService = Depends(UserService),
) -> UserInDB:
    return await user_service.create_user_from_token(uow, token)
