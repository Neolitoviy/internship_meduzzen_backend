class UserException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UserNotFound(UserException):
    """Exception raised when user is not found."""

    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404)


class UserAlreadyExists(UserException):
    """Exception raised when user already exists."""

    def __init__(self, message: str = "User already exists"):
        super().__init__(message, status_code=409)


class EmailAlreadyExists(UserException):
    """Exception raised when email already exists."""

    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, status_code=409)
