import jwt
from fastapi import HTTPException

from app.core.config import settings


class VerifyToken:
    """
    A class to handle the verification of JWT tokens using Auth0.

    Attributes:
        token (str): The JWT token to be verified.
        jwks_url (str): The URL to fetch JSON Web Key Set (JWKS) from Auth0.
        jwks_client (jwt.PyJWKClient): A client to fetch and manage JWKS.

    Methods:
        verify() -> dict: Verifies the JWT token and returns its payload.
    """
    def __init__(self, token: str):
        """
        Initializes the VerifyToken class with the given token.

        Args:
            token (str): The JWT token to be verified.
        """
        self.token = token
        self.jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(self.jwks_url)

    def verify(self) -> dict:
        """
        Verifies the JWT token and returns its payload.

        Returns:
            dict: The decoded payload of the JWT token.

        Raises:
            HTTPException: If the token verification fails due to client errors or decoding errors.
        """
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
