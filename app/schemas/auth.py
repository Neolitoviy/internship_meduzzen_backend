from pydantic import BaseModel, EmailStr, Field


class UserAuthBase(BaseModel):
    """
    Base model for user authentication information.
    """
    email: EmailStr = Field(..., description="The email address of the user.")


class UserAuthCreate(UserAuthBase):
    """
    Model for creating a new user with authentication information.
    """
    password: str = Field(..., description="The password for the user.")


class SignInRequest(BaseModel):
    """
    Model for user sign-in request.
    """
    email: EmailStr = Field(..., description="The email address of the user.")
    password: str = Field(..., description="The password for the user.")
