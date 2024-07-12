import logging
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.db.postgres_db import check_postgres_connection
from app.db.redis_db import check_redis_connection
from app.core.logging_config import logging_config

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health check"],
)


@router.get("/")
async def health_check():
    logger.info("Health check endpoint was called")
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@router.get("/postgres")
async def health_check_postgres(session: AsyncSession = Depends(get_session)):
    postgres_status = await check_postgres_connection(session)
    return {
        "postgresql": "connected" if postgres_status is True else f"error: {postgres_status}",
    }


@router.get("/redis")
async def health_check_redis():
    redis_status = await check_redis_connection()
    return {
        "redis": "connected" if redis_status else f"error: {redis_status}",
    }
