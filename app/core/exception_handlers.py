from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from starlette import status
from app.core.exceptions import UserNotFound, UserAlreadyExists, EmailAlreadyExists, CompanyNotFound, \
    CompanyPermissionError


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(UserNotFound)
    async def user_not_found_exception_handler(request: Request, exc: UserNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(EmailAlreadyExists)
    async def email_already_exists_exception_handler(request: Request, exc: EmailAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_exception_handler(request: Request, exc: UserAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(CompanyNotFound)
    async def company_not_found_exception_handler(request: Request, exc: CompanyNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(CompanyPermissionError)
    async def company_permission_error_exception_handler(request: Request, exc: CompanyPermissionError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )
