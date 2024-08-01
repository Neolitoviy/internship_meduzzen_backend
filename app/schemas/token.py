from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    Represents an authentication token.
    """
    access_token: str = Field(..., description="The actual JWT token.")
    token_type: str = Field(..., description="The type of the token, typically 'Bearer'.")
    expiration: int = Field(..., description="The expiration timestamp of the token.")


class TokenData(BaseModel):
    """
    Represents the data within a token.
    """
    email: Optional[str] = Field(None, description="The email associated with the token, if any.")
