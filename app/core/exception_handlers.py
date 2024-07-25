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
    @app.exception_handler(UserNotFound)
    async def user_not_found_exception_handler(request: Request, exc: UserNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(EmailAlreadyExists)
    async def email_already_exists_exception_handler(
            request: Request, exc: EmailAlreadyExists
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(CompanyPermissionError)
    async def company_permission_error_exception_handler(
            request: Request, exc: CompanyPermissionError
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(InvalidCredentials)
    async def invalid_credentials_exception_handler(
            request: Request, exc: InvalidCredentials
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message},
        )

    @app.exception_handler(PermissionDenied)
    async def permission_denied_exception_handler(
            request: Request, exc: PermissionDenied
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message},
        )

    @app.exception_handler(BadRequest)
    async def bad_request_exception_handler(request: Request, exc: BadRequest):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(RecordNotFound)
    async def record_not_found_handler(request: Request, exc: RecordNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
        )

    @app.exception_handler(AddRecordError)
    async def add_record_handler(request: Request, exc: AddRecordError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
        )

    @app.exception_handler(NoResultFound)
    async def no_result_found_handler(request: Request, exc: NoResultFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
