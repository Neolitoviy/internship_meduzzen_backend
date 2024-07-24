import jwt
from fastapi import HTTPException

from app.core.config import settings


class VerifyToken:
    def __init__(self, token: str):
        self.token = token
        self.jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(self.jwks_url)

    def verify(self) -> dict:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            raise HTTPException(status_code=401, detail=str(error))
        except jwt.exceptions.DecodeError as error:
            raise HTTPException(status_code=401, detail=str(error))

        try:
            payload = jwt.decode(
                self.token,
                signing_key,
                algorithms=[settings.auth0_algorithms],
                audience=settings.auth0_api_audience,
                issuer=f"https://{settings.auth0_domain}/",
            )
        except jwt.PyJWTError as error:
            raise HTTPException(status_code=401, detail=str(error))

        return payload
