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
    """
    Service for managing user operations.
    """
    @staticmethod
    async def create_user(uow: IUnitOfWork, user: UserCreate) -> UserResponse:
        """
        Create a new user.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            user (UserCreate): The user data for creating a new user.

        Raises:
            EmailAlreadyExists: If a user with the same email already exists.

        Returns:
            UserResponse: The created user.
        """
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
        """
        Retrieve a list of users with pagination.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            skip (int): The number of records to skip.
            limit (int): The number of records to retrieve.
            request_url (str): The request URL for pagination.

        Returns:
            UserListResponse: A paginated list of users.
        """
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
        """
        Retrieve a user by their ID.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            user_id (int): The ID of the user to retrieve.

        Returns:
            UserResponse: The user data.
        """
        async with uow:
            user = await uow.users.find_one(id=user_id)
            return UserResponse.model_validate(user)

    @staticmethod
    async def get_user_by_email(uow: IUnitOfWork, email: str) -> UserInDB:
        """
        Retrieve a user by their email.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            email (str): The email of the user to retrieve.

        Returns:
            UserInDB: The user data.
        """
        async with uow:
            user = await uow.users.find_one(email=email)
            return UserInDB.model_validate(user)

    @staticmethod
    async def update_user(
        uow: IUnitOfWork,
        user: UserUpdate,
        current_user_id: int,
    ) -> UserResponse:
        """
        Update a user's information.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            user (UserUpdate): The updated user data.
            current_user_id (int): The ID of the current user.

        Returns:
            UserResponse: The updated user data.
        """
        user_dict = user.model_dump(exclude_unset=True)
        async with uow:
            updated_user = await uow.users.edit_one(current_user_id, user_dict)
            return UserResponse.model_validate(updated_user)

    @staticmethod
    async def delete_user(uow: IUnitOfWork, current_user_id: int) -> None:
        """
        Deactivate a user account.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            current_user_id (int): The ID of the current user.
        """
        async with uow:
            await uow.users.edit_one(current_user_id, {"is_active": False})

    @staticmethod
    async def authenticate_user(
        uow: IUnitOfWork, email: str, password: str
    ) -> Optional[Token]:
        """
        Authenticate a user and generate an access token.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            email (str): The user's email.
            password (str): The user's password.

        Raises:
            UserNotFound: If the user account is deactivated.
            InvalidCredentials: If the email or password is incorrect.

        Returns:
            Optional[Token]: The generated access token.
        """
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
        """
        Create a new user from a token.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            token (HTTPAuthorizationCredentials): The authorization token.

        Raises:
            BadRequest: If the token is invalid.

        Returns:
            UserInDB: The created user.
        """
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
        """
        Retrieve the email from a token. check_owner_jwt_type for default or Auth0 Authorization.

        Args:
            token (HTTPAuthorizationCredentials): The authorization token.

        Returns:
            Optional[str]: The email from the token.
        """
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
        """
        Check if the current user has permission to perform an action with user_id user.

        Args:
            user_id (int): The ID of the user to check.
            current_user_id (int): The ID of the current user.

        Raises:
            PermissionDenied: If the current user does not have permission.
        """
        if user_id != current_user_id:
            raise PermissionDenied("You don't have permission!")
