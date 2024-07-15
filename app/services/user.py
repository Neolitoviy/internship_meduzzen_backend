from typing import Optional
from fastapi.security import HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.hashing import Hasher
from app.core.verify_token import VerifyToken
from app.schemas.auth import UserAuthCreate
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserInDB, UserListResponse, PaginationLinks
from app.services.jwt import check_jwt_type, decode_jwt_token, create_jwt_token
from app.utils.unitofwork import IUnitOfWork
from datetime import datetime, timedelta
import logging
from app.core.logging_config import logging_config
from app.core.exceptions import UserNotFound, EmailAlreadyExists, InvalidCredentials, BadRequest, PermissionDenied

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def create_user(uow: IUnitOfWork, user: UserCreate) -> UserResponse:
        user_dict = user.model_dump()
        user_dict.pop('password1', None)
        user_dict.pop('password2', None)
        async with uow:
            existing_user = await uow.users.find_one(email=user_dict['email'])
            if existing_user:
                raise EmailAlreadyExists(f"User with email {user_dict['email']} already exists")
            new_user = await uow.users.add_one(user_dict)
            await uow.commit()
            return UserResponse(**new_user)

    @staticmethod
    async def get_users(uow: IUnitOfWork, skip: int, limit: int, request_url: str) -> UserListResponse:
        async with uow:
            total_users = await uow.users.count_all()
            users = await uow.users.find_all(skip=skip, limit=limit)
            total_pages = (total_users + limit - 1) // limit
            current_page = (skip // limit) + 1

            base_url = request_url.split('?')[0]
            previous_page_url = f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}" if current_page > 1 else None
            next_page_url = f"{base_url}?skip={skip + limit}&limit={limit}" if current_page < total_pages else None

            return UserListResponse(
                total_pages=total_pages,
                current_page=current_page,
                users=[UserResponse.model_validate(user) for user in users],
                pagination=PaginationLinks(
                    previous=previous_page_url,
                    next=next_page_url
                )
            )

    @staticmethod
    async def get_user_by_id(uow: IUnitOfWork, user_id: int) -> UserResponse:
        async with uow:
            user = await uow.users.find_one(id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")
            return UserResponse(**user.__dict__)

    @staticmethod
    async def get_user_by_email(uow: IUnitOfWork, email: str) -> UserInDB:
        async with uow:
            user = await uow.users.find_one(email=email)
            if not user:
                raise UserNotFound(f"User with email {email} not found")
            return UserInDB(**user.__dict__)

    async def update_user(self, uow: IUnitOfWork, user_id: int, user: UserUpdate, current_user_id: int) -> UserResponse:
        await self.check_user_permission(user_id, current_user_id)
        user_dict = user.model_dump(exclude_unset=True)
        async with uow:
            updated_user = await uow.users.edit_one(user_id, user_dict)
            if not updated_user:
                raise UserNotFound(f"User with id {user_id} not found")
            await uow.commit()
            return UserResponse(**updated_user)

    async def delete_user(self, uow: IUnitOfWork, user_id: int, current_user_id: int) -> UserResponse:
        await self.check_user_permission(user_id, current_user_id)
        async with uow:
            user = await uow.users.find_one(id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")
            await uow.users.delete_one(user_id)
            await uow.commit()
            return UserResponse(**user.__dict__)

    @staticmethod
    async def authenticate_user(uow: IUnitOfWork, email: str, password: str) -> Optional[Token]:
        async with uow:
            user = await uow.users.find_one(email=email)
            if user is None or not Hasher.verify_password(password, user.hashed_password):
                raise InvalidCredentials("Invalid email or password")
            access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
            access_token = create_jwt_token(data={"sub": str(user.id), "email": user.email, "owner": settings.owner},
                                            expires_delta=access_token_expires)
            return Token(access_token=access_token, token_type="Bearer",
                         expiration=datetime.utcnow() + access_token_expires)

    @staticmethod
    async def create_user_from_token(uow: IUnitOfWork, token: HTTPAuthorizationCredentials) -> UserInDB:
        current_email = await UserService.get_email_from_token(token)
        async with uow:
            user = await uow.users.find_one(email=current_email)
            if user is None and current_email is None:
                raise BadRequest("Invalid token")
            if not user:
                user_data = UserAuthCreate(email=current_email, password=str(datetime.utcnow()))
                user = await UserService.create_user(uow, user=UserCreate.model_validate(user_data))
            return UserInDB.model_validate(user)

    @staticmethod
    async def get_email_from_token(token: HTTPAuthorizationCredentials) -> Optional[str]:
        check_owner_jwt_type = check_jwt_type(token)
        if check_owner_jwt_type:
            payload = decode_jwt_token(token.credentials)
            email = payload.get('email')
        else:
            payload = VerifyToken(token.credentials).verify()
            email = payload.get('email')
        return email

    @staticmethod
    async def check_user_permission(user_id: int, current_user_id: int) -> None:
        if user_id != current_user_id:
            raise PermissionDenied("You don't have permission!")
