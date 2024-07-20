from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
import time


class QuizResultCreate(BaseModel):
    user_id: int
    quiz_id: int
    company_id: int
    total_questions: int
    total_answers: int
    score: float

    model_config = {
        'from_attributes': True
    }


class QuizResultResponse(QuizResultCreate):
    id: int
    created_at: datetime


class QuizVoteRequest(BaseModel):
    answers: Dict[int, int]


class UserQuizVote(BaseModel):
    user_id: int
    company_id: int
    quiz_id: int
    question_id: int
    question_text: str
    answer_text: str
    is_correct: bool
    timestamp: Optional[float] = Field(default_factory=lambda: time.time())
