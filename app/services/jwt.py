from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import jwt

from app.core.config import settings


def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create a JSON Web Token (JWT). timedelta(hours=3) for my time zone -> change if needs.

    Args:
        data (dict): The data to encode into the token.
        expires_delta (timedelta): The time delta for when the token expires.

    Returns:
        str: The encoded JWT.
    """
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
    """
    Decode a JSON Web Token (JWT).

    Args:
        token (Optional[Union[HTTPAuthorizationCredentials, str]]): The token to decode.

    Returns:
        dict: The decoded payload.

    Raises:
        HTTPException: If the signature verification fails, for example: token expire.
    """
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
    """
    Check the type of JSON Web Token (JWT) -> Default token is owner -> Auth0 token is None.

    Args:
        token (Optional[HTTPAuthorizationCredentials]): The token to check.

    Returns:
        Optional[bool]: The owner field from the token claims if present, otherwise None.

    Raises:
        HTTPException: If the token is not found or the request is bad.
    """
    try:
        token_view = jwt.get_unverified_claims(token.credentials)
        owner = token_view.get("owner", None)
        return owner
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Not Found or Bad Request")
