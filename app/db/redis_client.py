import asyncio_redis
import json

from app.core.config import settings
from app.schemas.quiz_result import QuizVoteCreate


async def get_redis_client():
    return await asyncio_redis.Connection.create(host=settings.redis_host, port=settings.redis_port)


async def save_quiz_vote_to_redis(vote: QuizVoteCreate) -> None:
    client = await get_redis_client()
    key = f"quiz_vote:{vote.user_id}:{vote.company_id}:{vote.quiz_id}:{vote.question_id}"
    vote_data = vote.dict()
    await client.setex(key, 48 * 3600, json.dumps(vote_data))
