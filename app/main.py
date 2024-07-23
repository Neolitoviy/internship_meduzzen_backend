import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.db.redis_db import get_redis_client
from app.routers.user import router as users_router
from app.routers.healthcheck import router as health_router
from app.routers.company import router as company_router
from app.routers.company_invitation import router as company_invitation_router
from app.routers.company_request import router as company_request_router
from app.routers.quiz import router as quiz_router
from app.routers.question import router as question_router
from app.routers.answer import router as answer_router
from app.routers.me import router as me_router
from app.routers.quiz_result import router as quiz_result_router
from app.core.logging_config import logging_config
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

register_exception_handlers(app)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All
    allow_credentials=True,
    allow_methods=["*"],  # All
    allow_headers=["*"],  # All
)


@app.on_event("startup")
async def startup_event():
    client = await get_redis_client()
    await client.ping()


@app.on_event("shutdown")
async def shutdown_event():
    client = await get_redis_client()
    await client.close()


# Routes
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