import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
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


@app.get("/base_status")
async def base_status():
    postgres_status = await check_postgres_connection()
    redis_status = await check_redis_connection()
    return {
        'postgres_status': "connected" if postgres_status is True else f"error: {postgres_status}",
        'redis_status': "connected" if redis_status == 1 else f"error: {redis_status}"
    }


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
