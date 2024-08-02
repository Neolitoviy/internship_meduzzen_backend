from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import jwt

from app.core.config import settings
from app.services.jwt import check_jwt_type, create_jwt_token, decode_jwt_token


@pytest.fixture
def test_data():
    return {"sub": "testuser", "owner": True}


@pytest.fixture
def test_token(test_data):
    return create_jwt_token(test_data, timedelta(minutes=30))


def test_create_jwt_token(test_data):
    token = create_jwt_token(test_data, timedelta(minutes=30))
    assert isinstance(token, str)

    decoded_payload = jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    assert decoded_payload["sub"] == "testuser"
    assert decoded_payload["owner"] == True


def test_decode_jwt_token(test_token, test_data):
    decoded_payload = decode_jwt_token(test_token)
    assert decoded_payload["sub"] == test_data["sub"]
    assert decoded_payload["owner"] == test_data["owner"]

    with pytest.raises(HTTPException):
        decode_jwt_token("invalid_token")


def test_check_jwt_type(test_token, test_data):
    mock_credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=test_token
    )
    assert check_jwt_type(mock_credentials) == test_data["owner"]

    with pytest.raises(HTTPException):
        check_jwt_type(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        )
