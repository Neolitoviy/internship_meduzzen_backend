from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from starlette import status

from app.core.exceptions import (
    AddRecordError,
    BadRequest,
    CompanyPermissionError,
    EmailAlreadyExists,
    InvalidCredentials,
    PermissionDenied,
    RecordNotFound,
    UserNotFound,
)


def register_exception_handlers(app: FastAPI):
    """
    Registers custom exception handlers for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """

    @app.exception_handler(UserNotFound)
    async def user_not_found_exception_handler(request: Request, exc: UserNotFound):
        """
        Handles UserNotFound exceptions.

        Args:
            request (Request): The incoming request.
            exc (UserNotFound): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 404 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(EmailAlreadyExists)
    async def email_already_exists_exception_handler(
        request: Request, exc: EmailAlreadyExists
    ):
        """
        Handles EmailAlreadyExists exceptions.

        Args:
            request (Request): The incoming request.
            exc (EmailAlreadyExists): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 409 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(CompanyPermissionError)
    async def company_permission_error_exception_handler(
        request: Request, exc: CompanyPermissionError
    ):
        """
        Handles CompanyPermissionError exceptions.

        Args:
            request (Request): The incoming request.
            exc (CompanyPermissionError): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 403 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(InvalidCredentials)
    async def invalid_credentials_exception_handler(
        request: Request, exc: InvalidCredentials
    ):
        """
        Handles InvalidCredentials exceptions.

        Args:
            request (Request): The incoming request.
            exc (InvalidCredentials): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 401 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message},
        )

    @app.exception_handler(PermissionDenied)
    async def permission_denied_exception_handler(
        request: Request, exc: PermissionDenied
    ):
        """
        Handles PermissionDenied exceptions.

        Args:
            request (Request): The incoming request.
            exc (PermissionDenied): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 403 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message},
        )

    @app.exception_handler(BadRequest)
    async def bad_request_exception_handler(request: Request, exc: BadRequest):
        """
        Handles BadRequest exceptions.

        Args:
            request (Request): The incoming request.
            exc (BadRequest): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 400 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(RecordNotFound)
    async def record_not_found_handler(request: Request, exc: RecordNotFound):
        """
        Handles RecordNotFound exceptions.

        Args:
            request (Request): The incoming request.
            exc (RecordNotFound): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 404 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
        )

    @app.exception_handler(AddRecordError)
    async def add_record_handler(request: Request, exc: AddRecordError):
        """
        Handles AddRecordError exceptions.

        Args:
            request (Request): The incoming request.
            exc (AddRecordError): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 404 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
        )

    @app.exception_handler(NoResultFound)
    async def no_result_found_handler(request: Request, exc: NoResultFound):
        """
        Handles NoResultFound exceptions.

        Args:
            request (Request): The incoming request.
            exc (NoResultFound): The exception instance.

        Returns:
            JSONResponse: A JSON response with a 404 status code and error detail.
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
