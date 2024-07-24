from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.core.exceptions import (
    BadRequest,
    CompanyNotFound,
    CompanyPermissionError,
    EmailAlreadyExists,
    InvalidCredentials,
    InvitationNotFound,
    MemberNotFound,
    PermissionDenied,
    RequestNotFound,
    UserAlreadyExists,
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

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_exception_handler(
        request: Request, exc: UserAlreadyExists
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(CompanyNotFound)
    async def company_not_found_exception_handler(
        request: Request, exc: CompanyNotFound
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(CompanyPermissionError)
    async def company_permission_error_exception_handler(
        request: Request, exc: CompanyPermissionError
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(InvitationNotFound)
    async def invitation_not_found_exception_handler(
        request: Request, exc: InvitationNotFound
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(MemberNotFound)
    async def member_not_found_exception_handler(request: Request, exc: MemberNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(RequestNotFound)
    async def request_not_found_exception_handler(
        request: Request, exc: RequestNotFound
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
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
