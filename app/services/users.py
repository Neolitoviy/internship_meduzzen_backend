from app.schemas.users import UserCreate, UserUpdate, UserResponse, UserInDB, UserListResponse, PaginationLinks
from app.utils.unitofwork import IUnitOfWork
from datetime import datetime
import logging
from app.core.logging_config import logging_config
from app.core.exceptions import UserNotFound, EmailAlreadyExists

logger = logging.getLogger(__name__)


class UsersService:
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

    @staticmethod
    async def update_user(uow: IUnitOfWork, user_id: int, user: UserUpdate) -> UserResponse:
        user_dict = user.model_dump(exclude_unset=True)
        async with uow:
            updated_user = await uow.users.edit_one(user_id, user_dict)
            if not updated_user:
                raise UserNotFound(f"User with id {user_id} not found")
            await uow.commit()
            return UserResponse(**updated_user)

    @staticmethod
    async def delete_user(uow: IUnitOfWork, user_id: int) -> UserResponse:
        async with uow:
            user = await uow.users.find_one(id=user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")
            await uow.users.delete_one(user_id)
            await uow.commit()
            return UserResponse(**user.__dict__)
