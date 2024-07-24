from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import jwt

from app.core.config import settings


def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = int((datetime.utcnow() + expires_delta + timedelta(hours=3)).timestamp())
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_jwt_token(
    token: Optional[Union[HTTPAuthorizationCredentials, str]] = None
) -> dict:
    try:
        if isinstance(token, HTTPAuthorizationCredentials):
            token = token.credentials
        decoded_payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return decoded_payload
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Signature verification failed.")


def check_jwt_type(
    token: Optional[HTTPAuthorizationCredentials] = None,
) -> Optional[bool]:
    try:
        token_view = jwt.get_unverified_claims(token.credentials)
        owner = token_view.get("owner", None)
        return owner
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Not Found or Bad Request")
