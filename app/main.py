import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_session
from app.db.postgres_db import check_postgres_connection
from app.db.redis_db import check_redis_connection

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All
    allow_credentials=True,
    allow_methods=["*"],  # All
    allow_headers=["*"],  # All
)


@app.get("/")
async def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@app.get("/health/postgres")
async def health_check_postgres(session: AsyncSession = Depends(get_session)):
    postgres_status = await check_postgres_connection(session)
    return {
        "postgresql": "connected" if postgres_status is True else f"error: {postgres_status}",
    }


@app.get("/health/redis")
async def health_check_redis():
    redis_status = await check_redis_connection()
    return {
        "redis": "connected" if redis_status else f"error: {redis_status}",
    }


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
