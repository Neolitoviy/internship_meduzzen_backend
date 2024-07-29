import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.exceptions import (
    BadRequest,
    EmailAlreadyExists,
    InvalidCredentials,
    PermissionDenied,
    UserNotFound,
)
from app.core.hashing import Hasher
from app.core.logging_config import logging_config
from app.core.verify_token import VerifyToken
from app.schemas.auth import UserAuthCreate
from app.schemas.token import Token
from app.schemas.user import (
    UserCreate,
    UserInDB,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.jwt import check_jwt_type, create_jwt_token, decode_jwt_token
from app.utils.pagination import paginate
from app.utils.unitofwork import IUnitOfWork

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def create_user(uow: IUnitOfWork, user: UserCreate) -> UserResponse:
        user_dict = user.model_dump()
        async with uow:
            if await uow.users.find_one_or_none(email=user_dict["email"]):
                raise EmailAlreadyExists(
                    f"User with email {user_dict['email']} already exists"
                )
            new_user = await uow.users.add_one(user_dict)
            return UserResponse.model_validate(new_user)

    @staticmethod
    async def get_users(
        uow: IUnitOfWork, skip: int, limit: int, request_url: str
    ) -> UserListResponse:
        async with uow:
            total_users = await uow.users.count_all()
            users = await uow.users.find_all(skip=skip, limit=limit)

            users_response = [UserResponse.model_validate(user) for user in users]
            pagination_response = paginate(
                items=users_response,
                total_items=total_users,
                skip=skip,
                limit=limit,
                request_url=request_url,
            )

            return UserListResponse(
                total_pages=pagination_response.total_pages,
                current_page=pagination_response.current_page,
                items=pagination_response.items,
                pagination=pagination_response.pagination,
            )

    @staticmethod
    async def get_user_by_id(uow: IUnitOfWork, user_id: int) -> UserResponse:
        async with uow:
            user = await uow.users.find_one(id=user_id)
            return UserResponse.model_validate(user)

    @staticmethod
    async def get_user_by_email(uow: IUnitOfWork, email: str) -> UserInDB:
        async with uow:
            user = await uow.users.find_one(email=email)
            return UserInDB.model_validate(user)

    @staticmethod
    async def update_user(
        uow: IUnitOfWork,
        user: UserUpdate,
        current_user_id: int,
    ) -> UserResponse:
        user_dict = user.model_dump(exclude_unset=True)
        async with uow:
            updated_user = await uow.users.edit_one(current_user_id, user_dict)
            return UserResponse.model_validate(updated_user)

    @staticmethod
    async def delete_user(uow: IUnitOfWork, current_user_id: int) -> None:
        async with uow:
            await uow.users.edit_one(current_user_id, {"is_active": False})

    @staticmethod
    async def authenticate_user(
        uow: IUnitOfWork, email: str, password: str
    ) -> Optional[Token]:
        async with uow:
            user = await uow.users.find_one(email=email)
            if not user.is_active:
                raise UserNotFound("Account is deactivated")
            if not Hasher.verify_password(password, user.hashed_password):
                raise InvalidCredentials("Invalid email or password")
            access_token_expires = timedelta(
                minutes=settings.jwt_access_token_expire_minutes
            )
            access_token = create_jwt_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "owner": settings.owner,
                },
                expires_delta=access_token_expires,
            )
            expiration_timestamp = int(
                (
                    datetime.utcnow() + access_token_expires + timedelta(hours=3)
                ).timestamp()
            )
            return Token(
                access_token=access_token,
                token_type="Bearer",
                expiration=expiration_timestamp,
            )

    @staticmethod
    async def create_user_from_token(
        uow: IUnitOfWork, token: HTTPAuthorizationCredentials
    ) -> UserInDB:
        current_email = await UserService.get_email_from_token(token)
        async with uow:
            user = await uow.users.find_one_or_none(email=current_email)
            if user is None and current_email is None:
                raise BadRequest("Invalid token")
            if not user:
                user_data = UserAuthCreate(
                    email=current_email, password=str(datetime.utcnow())
                )
                user = await UserService.create_user(
                    uow, user=UserCreate.model_validate(user_data)
                )
            return UserInDB.model_validate(user)

    @staticmethod
    async def get_email_from_token(
        token: HTTPAuthorizationCredentials,
    ) -> Optional[str]:
        check_owner_jwt_type = check_jwt_type(token)
        if check_owner_jwt_type:
            payload = decode_jwt_token(token.credentials)
            email = payload.get("email")
        else:
            payload = VerifyToken(token.credentials).verify()
            email = payload.get("email")
        return email

    @staticmethod
    async def check_user_permission(user_id: int, current_user_id: int) -> None:
        if user_id != current_user_id:
            raise PermissionDenied("You don't have permission!")
