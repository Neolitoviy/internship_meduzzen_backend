class UserCreationError(Exception):
    """Exception raised when an error occurs during user creation."""

    def __init__(self, message="Failed to create user", errors=None):
        super().__init__(message)
        self.errors = errors


class UserNotFoundError(Exception):
    """Exception raised when the user cannot be found."""

    def __init__(self, message="User not found"):
        super().__init__(message)


class UserUpdateError(Exception):
    """Exception raised when there is an error updating the user."""

    def __init__(self, message="Failed to update user"):
        super().__init__(message)


class UserDeletionError(Exception):
    """Exception raised when there is an error deleting the user."""

    def __init__(self, message="Failed to delete user"):
        super().__init__(message)


class UserFetchError(Exception):
    """Exception raised when there is an error fetching the user list."""

    def __init__(self, message="Failed to fetch users"):
        super().__init__(message)
