from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.exceptions import BadRequest
from app.core.hashing import Hasher
from app.utils.pagination import PaginationResponse


class UserBase(BaseModel):
    """
    Base model for user data.
    """
    email: EmailStr = Field(..., description="User's email address.")
    firstname: Optional[str] = Field(None, description="User's first name.")
    lastname: Optional[str] = Field(None, description="User's last name.")
    city: Optional[str] = Field(None, description="User's city.")
    phone: Optional[str] = Field(None, description="User's phone number.")
    avatar: Optional[str] = Field(None, description="User's avatar URL.")
    is_active: Optional[bool] = Field(True, description="Status indicating if the user is active.")
    is_superuser: Optional[bool] = Field(False, description="Status indicating if the user is a superuser.")

    model_config = {"from_attributes": True}


class UserCreateInput(UserBase):
    """
    Input model for creating a user.
    """
    password1: Optional[str] = Field(None, min_length=6, description="First password entry.")
    password2: Optional[str] = Field(None, min_length=6, description="Second password entry.")

    @model_validator(mode="before")
    @classmethod
    def check_passwords_match(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the two passwords match.

        Args:
            values (Dict[str, Any]): The input values.

        Raises:
            BadRequest: If the passwords do not match.

        Returns:
            Dict[str, Any]: The validated values.
        """
        if (
            values.get("password1")
            and values.get("password2")
            and values["password1"] != values["password2"]
        ):
            raise BadRequest("Passwords do not match")
        return values


class UserCreate(UserBase):
    """
    Model for creating a user.
    """
    password1: Optional[str] = Field(None, min_length=6, exclude=True, description="First password entry.")
    password2: Optional[str] = Field(None, min_length=6, exclude=True, description="Second password entry.")
    hashed_password: Optional[str] = Field(None, description="Hashed password.")

    @model_validator(mode="before")
    def hash_password(cls, values: Any) -> Any:
        """
        Hash the provided password.

        Args:
            values (Any): The input values.

        Returns:
            Any: The values with the hashed password.
        """
        values_dict = values.model_dump(exclude_unset=True)
        if "password1" in values_dict and values_dict["password1"]:
            hashed_password = Hasher.get_password_hash(values_dict["password1"])
            values_dict["hashed_password"] = hashed_password
        return values_dict

    model_config = {"from_attributes": True}


class UserUpdateInput(BaseModel):
    """
    Input model for updating a user.
    """
    firstname: Optional[str] = Field(None, description="User's first name.")
    lastname: Optional[str] = Field(None, description="User's last name.")
    password: Optional[str] = Field(None, min_length=6, description="User's new password.")


class UserUpdate(UserUpdateInput):
    """
    Model for updating a user.
    """
    password: Optional[str] = Field(None, min_length=6, exclude=True, description="User's new password.")
    hashed_password: Optional[str] = Field(None, description="Hashed password.")

    @model_validator(mode="before")
    def hash_password(cls, values: Any) -> Any:
        """
        Hash the provided password.

        Args:
            values (Any): The input values.

        Returns:
            Any: The values with the hashed password.
        """
        values_dict = values.model_dump(exclude_unset=True)
        if "password" in values_dict and values_dict["password"] is not None:
            hashed_password = Hasher.get_password_hash(values_dict["password"])
            values_dict["hashed_password"] = hashed_password
        return values_dict

    model_config = {"from_attributes": True}


class UserInDB(UserBase):
    """
    Model representing a user in the database.
    """
    id: int = Field(..., description="User ID.")
    hashed_password: Optional[str] = Field(None, description="Hashed password.")
    created_at: datetime = Field(..., description="Timestamp when the user was created.")
    updated_at: datetime = Field(..., description="Timestamp when the user was last updated.")


class UserResponse(UserBase):
    """
    Model for user response.
    """
    id: int = Field(..., description="User ID.")
    created_at: datetime = Field(..., description="Timestamp when the user was created.")
    updated_at: datetime = Field(..., description="Timestamp when the user was last updated.")

    model_config = {"from_attributes": True}


class UserListResponse(PaginationResponse):
    """
    Model for a paginated list of users.
    """
    items: List[UserResponse] = Field(..., description="List of user responses.")

    model_config = {"from_attributes": True}
