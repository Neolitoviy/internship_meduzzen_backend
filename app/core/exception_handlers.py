from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import UserNotFound, EmailAlreadyExists, UserAlreadyExists


async def user_not_found_exception_handler(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


async def email_already_exists_exception_handler(request: Request, exc: EmailAlreadyExists):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


async def user_already_exists_exception_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )
