class UserNotFound(Exception):
    """
    Exception raised when a user is not found.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class EmailAlreadyExists(Exception):
    """
    Exception raised when attempting to create a user with an email that already exists.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CompanyPermissionError(Exception):
    """
    Exception raised when a user does not have the necessary permissions to perform an action on a company.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidCredentials(Exception):
    """
    Exception raised when the provided credentials are invalid.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PermissionDenied(Exception):
    """
    Exception raised when a user does not have the required permissions to perform an action.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BadRequest(Exception):
    """
    Exception raised when the request is invalid or malformed.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RecordNotFound(Exception):
    """
    Exception raised when a record is not found in the database.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AddRecordError(Exception):
    """
    Exception raised when there is an error adding a record to the database.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
