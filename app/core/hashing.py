from passlib.context import CryptContext

# Initialize CryptContext with bcrypt hashing scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    """
    Hasher class provides static methods to hash passwords and verify hashed passwords.
    """
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
        -----
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to verify against.

        Returns:
        --------
        bool: True if the plain password matches the hashed password, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a plain password.

        Args:
        -----
        password (str): The plain text password to hash.

        Returns:
        --------
        str: The hashed password.
        """
        return pwd_context.hash(password)
