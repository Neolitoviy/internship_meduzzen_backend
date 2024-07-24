from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    expiration: int  # timestamp


class TokenData(BaseModel):
    email: Optional[str] = None
