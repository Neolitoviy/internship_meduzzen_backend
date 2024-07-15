from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    expiration: datetime  # Додане поле expiration


class TokenData(BaseModel):
    email: Optional[str] = None