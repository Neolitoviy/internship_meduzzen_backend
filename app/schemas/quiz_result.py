import time
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


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


class UserQuizVote(BaseModel):
    user_id: int
    company_id: int
    quiz_id: int
    question_id: int
    question_text: str
    answer_text: str
    is_correct: bool
    timestamp: Optional[float] = Field(default_factory=time.time)

    def to_csv_row(self):
        return [
            self.user_id,
            self.company_id,
            self.quiz_id,
            self.question_id,
            self.question_text,
            self.answer_text,
            self.is_correct,
            self.timestamp,
        ]
