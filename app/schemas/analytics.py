from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class QuizScore(BaseModel):
    quiz_id: int
    quiz_title: str
    scores: List[float]
    timestamps: List[datetime]


class LastQuizAttempt(BaseModel):
    quiz_id: int
    timestamp: datetime


class CompanyMemberAverageScore(BaseModel):
    user_id: int
    average_score: float
    start_date: datetime
    end_date: datetime


class QuizTrend(BaseModel):
    quiz_id: int
    quiz_title: str
    average_score: float
    start_date: datetime
    end_date: datetime


class CompanyUserLastAttempt(BaseModel):
    user_id: int
    last_attempt: Optional[datetime]
