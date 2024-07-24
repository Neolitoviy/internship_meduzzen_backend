from datetime import datetime
from typing import Dict

from pydantic import BaseModel


class QuizResultCreate(BaseModel):
    user_id: int
    quiz_id: int
    company_id: int
    total_questions: int
    total_answers: int
    score: float

    model_config = {"from_attributes": True}


class QuizResultResponse(QuizResultCreate):
    id: int
    created_at: datetime


class QuizVoteRequest(BaseModel):
    answers: Dict[int, int]
