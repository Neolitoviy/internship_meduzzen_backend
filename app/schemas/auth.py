from pydantic import BaseModel, EmailStr


class UserAuthBase(BaseModel):
    email: EmailStr


class UserAuthCreate(UserAuthBase):
    password: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str
