from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    phone_number: str = None
    age: int = None
    city: str = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str = None


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpRequest(UserCreate):
    pass


class UserDetail(UserResponse):
    pass


class UsersList(BaseModel):
    users: list[UserResponse]
    total: int
