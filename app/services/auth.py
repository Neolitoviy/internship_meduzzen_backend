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
    """
    Authenticate the user using a bearer token and return the authenticated user.

    Args:
        token (HTTPAuthorizationCredentials): Bearer token credentials. Defaults to dependency injection using HTTPBearer.
        uow (IUnitOfWork): Unit of work for database operations. Defaults to dependency injection using UnitOfWork.
        user_service (UserService): Service for user operations. Defaults to dependency injection using UserService.

    Returns:
        UserInDB: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user cannot be authenticated.
    """
    return await user_service.create_user_from_token(uow, token)
