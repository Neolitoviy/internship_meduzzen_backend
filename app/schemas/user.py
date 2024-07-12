from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime
from typing import Optional, Any, Dict, List
from app.core.hashing import Hasher


class UserBase(BaseModel):
    email: EmailStr
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    model_config = {
        'from_attributes': True
    }


class UserCreate(UserBase):
    password1: Optional[str] = Field(None, min_length=6)
    password2: Optional[str] = Field(None, min_length=6)
    hashed_password: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def check_passwords_match(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get('password1') and values.get('password2') and values['password1'] != values['password2']:
            raise ValueError('Passwords do not match')
        return values

    @model_validator(mode='before')
    @classmethod
    def hash_password(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get('password1'):
            values['hashed_password'] = Hasher.get_password_hash(values['password1'])
        return values

    model_config = {
        'from_attributes': True
    }


class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    password: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def hash_password(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if 'password' in values:
            values['hashed_password'] = Hasher.get_password_hash(values['password'])
            values.pop('password', None)
        return values

    @model_validator(mode='before')
    @classmethod
    def set_updated_at(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values['updated_at'] = datetime.utcnow()
        return values

    model_config = {
        'from_attributes': True
    }


class UserInDB(UserBase):
    id: int
    hashed_password: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        'from_attributes': True
    }


class PaginationLinks(BaseModel):
    previous: Optional[str]
    next: Optional[str]


class UserListResponse(BaseModel):
    current_page: int
    total_pages: int
    pagination: PaginationLinks
    users: List[UserResponse]

    model_config = {
        'from_attributes': True
    }
