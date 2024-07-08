from app.schemas.users import UserCreate, UserUpdate, UserResponse
from app.utils.security import hash_password
from app.utils.unitofwork import IUnitOfWork
from datetime import datetime
import logging
from app.core.logging_config import logging_config

logger = logging.getLogger(__name__)


class UsersService:
    @staticmethod
    async def add_user(uow: IUnitOfWork, user: UserCreate) -> UserResponse:
        user_dict = user.model_dump()
        user_dict["password"] = hash_password(user_dict["password"])
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        async with uow:
            user_id = await uow.users.add_one(user_dict)
            await uow.commit()
            user_dict["id"] = user_id
            return UserResponse(**user_dict)

    @staticmethod
    async def get_users(uow: IUnitOfWork, skip: int, limit: int) -> list[UserResponse]:
        async with uow:
            users = await uow.users.find_all(skip=skip, limit=limit)
            return [UserResponse(**user.__dict__) for user in users]

    @staticmethod
    async def get_user_by_id(uow: IUnitOfWork, user_id: int) -> UserResponse:
        async with uow:
            user = await uow.users.find_one(id=user_id)
            return UserResponse(**user.__dict__) if user else None

    @staticmethod
    async def update_user(uow: IUnitOfWork, user_id: int, user: UserUpdate) -> UserResponse:
        user_dict = user.model_dump(exclude_unset=True)
        if "password" in user_dict:
            user_dict["password"] = hash_password(user_dict["password"])
        user_dict["updated_at"] = datetime.utcnow()
        async with uow:
            await uow.users.edit_one(user_id, user_dict)
            await uow.commit()
            user = await uow.users.find_one(id=user_id)
            return UserResponse(**user.__dict__)

    @staticmethod
    async def delete_user(uow: IUnitOfWork, user_id: int) -> UserResponse:
        async with uow:
            user = await uow.users.find_one(id=user_id)
            await uow.users.delete_one(user_id)
            await uow.commit()
            return UserResponse(**user.__dict__)
