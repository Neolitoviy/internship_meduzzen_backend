from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import UserException


async def generic_exception_handler(request: Request, exc: UserException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )
