from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class QuizScore(BaseModel):
    """
    Model representing the scores of a quiz for a user.
    """
    quiz_id: int = Field(..., description="The unique identifier for the quiz.")
    quiz_title: str = Field(..., description="The title of the quiz.")
    scores: List[float] = Field(..., description="A list of scores the user has received for this quiz.")
    timestamps: List[datetime] = Field(..., description="A list of timestamps corresponding to when the scores were recorded.")


class LastQuizAttempt(BaseModel):
    """
    Model representing the last attempt of a quiz by a user.
    """
    quiz_id: int = Field(..., description="The unique identifier for the quiz.")
    timestamp: datetime = Field(..., description="The timestamp of the last attempt.")


class CompanyMemberAverageScore(BaseModel):
    """
    Model representing the average score of a company member over a period of time.
    """
    user_id: int = Field(..., description="The unique identifier for the user.")
    average_score: float = Field(..., description="The average score of the user.")
    start_date: datetime = Field(..., description="The start date of the period over which the average score is calculated.")
    end_date: datetime = Field(..., description="The end date of the period over which the average score is calculated.")


class QuizTrend(BaseModel):
    """
    Model representing the trend of quiz scores over a period of time.
    """
    quiz_id: int = Field(..., description="The unique identifier for the quiz.")
    quiz_title: str = Field(..., description="The title of the quiz.")
    average_score: float = Field(..., description="The average score of the quiz over the period.")
    start_date: datetime = Field(..., description="The start date of the period over which the trend is calculated.")
    end_date: datetime = Field(..., description="The end date of the period over which the trend is calculated.")


class CompanyUserLastAttempt(BaseModel):
    """
    Model representing the last attempt of a quiz by a user in company.
    """
    user_id: int = Field(..., description="The unique identifier for the user.")
    last_attempt: Optional[datetime] = Field(None, description="The timestamp of the last attempt, if any.")
