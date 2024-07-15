class UserNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExists(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class EmailAlreadyExists(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CompanyNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CompanyPermissionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidCredentials(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PermissionDenied(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BadRequest(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
