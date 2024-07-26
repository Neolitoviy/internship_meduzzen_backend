from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.hashing import Hasher
from app.utils.pagination import PaginationResponse


class UserBase(BaseModel):
    email: EmailStr
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    model_config = {"from_attributes": True}


class UserCreateInput(UserBase):
    password1: Optional[str] = Field(None, min_length=6)
    password2: Optional[str] = Field(None, min_length=6)

    @model_validator(mode="before")
    @classmethod
    def check_passwords_match(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if (
            values.get("password1")
            and values.get("password2")
            and values["password1"] != values["password2"]
        ):
            raise ValueError("Passwords do not match")
        return values


class UserCreate(UserBase):
    password1: Optional[str] = Field(None, min_length=6, exclude=True)
    password2: Optional[str] = Field(None, min_length=6, exclude=True)
    hashed_password: Optional[str] = None

    @model_validator(mode="before")
    def hash_password(cls, values: Any) -> Any:
        values_dict = values.model_dump(exclude_unset=True)
        if "password1" in values_dict and values_dict["password1"]:
            hashed_password = Hasher.get_password_hash(values_dict["password1"])
            values_dict["hashed_password"] = hashed_password
        return values_dict

    model_config = {"from_attributes": True}


class UserUpdateInput(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class UserUpdate(UserUpdateInput):
    password: Optional[str] = Field(None, min_length=6, exclude=True)
    hashed_password: Optional[str] = None

    @model_validator(mode="before")
    def hash_password(cls, values: Any) -> Any:
        values_dict = values.model_dump(exclude_unset=True)
        if "password" in values_dict and values_dict["password"] is not None:
            hashed_password = Hasher.get_password_hash(values_dict["password"])
            values_dict["hashed_password"] = hashed_password
        return values_dict

    model_config = {"from_attributes": True}


class UserInDB(UserBase):
    id: int
    hashed_password: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(PaginationResponse):
    items: List[UserResponse]

    model_config = {"from_attributes": True}
