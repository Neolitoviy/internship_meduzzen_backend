import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers.users import router as users_router
from app.routers.healthcheck import router as health_router
from app.core.logging_config import logging_config
import logging
from app.core.exception_handlers import (
    user_not_found_exception_handler,
    email_already_exists_exception_handler,
    user_already_exists_exception_handler,
)
from app.core.exceptions import UserNotFound, UserAlreadyExists, EmailAlreadyExists

app = FastAPI()

app.add_exception_handler(UserNotFound, user_not_found_exception_handler)
app.add_exception_handler(EmailAlreadyExists, email_already_exists_exception_handler)
app.add_exception_handler(UserAlreadyExists, user_already_exists_exception_handler)

logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All
    allow_credentials=True,
    allow_methods=["*"],  # All
    allow_headers=["*"],  # All
)

# Routes
app.include_router(users_router)
app.include_router(health_router)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
