import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers.users import router as users_router
from app.routers.healthcheck import router as health_router
from app.core.logging_config import logging_config
import logging
from app.core.exception_handlers import generic_exception_handler
from app.core.exceptions import UserNotFound, UserAlreadyExists, EmailAlreadyExists

app = FastAPI()

app.add_exception_handler(UserNotFound, generic_exception_handler)
app.add_exception_handler(EmailAlreadyExists, generic_exception_handler)
app.add_exception_handler(UserAlreadyExists, generic_exception_handler)

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
