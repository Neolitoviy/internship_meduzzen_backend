import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import logging_config
from app.db.redis_db import get_redis_client
from app.routers.answer import router as answer_router
from app.routers.company import router as company_router
from app.routers.company_invitation import router as company_invitation_router
from app.routers.company_request import router as company_request_router
from app.routers.healthcheck import router as health_router
from app.routers.me import router as me_router
from app.routers.question import router as question_router
from app.routers.quiz import router as quiz_router
from app.routers.quiz_result import router as quiz_result_router
from app.routers.user import router as users_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application lifespan events.

    Handles setup and teardown tasks such as establishing and closing Redis connections.
    """
    # startup
    client = await get_redis_client()
    await client.ping()
    yield
    # shutdown
    await client.close()


app = FastAPI(lifespan=lifespan)

# Register global exception handlers
register_exception_handlers(app)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(me_router)
app.include_router(users_router)
app.include_router(company_router)
app.include_router(company_invitation_router)
app.include_router(company_request_router)
app.include_router(quiz_router)
app.include_router(question_router)
app.include_router(answer_router)
app.include_router(quiz_result_router)
app.include_router(health_router)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)

