import time
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class QuizResultCreate(BaseModel):
    """
    Model representing the creation of a quiz result.
    """
    user_id: int = Field(..., description="ID of the user who took the quiz.")
    quiz_id: int = Field(..., description="ID of the quiz.")
    company_id: int = Field(..., description="ID of the company.")
    total_questions: int = Field(..., description="Total number of questions in the quiz.")
    total_answers: int = Field(..., description="Total number of answers given by the user.")
    score: float = Field(..., description="Score achieved by the user in the quiz.")

    model_config = {"from_attributes": True}


class QuizResultResponse(QuizResultCreate):
    """
    Model representing the response of a quiz result.
    """
    id: int = Field(..., description="ID of the quiz result.")
    created_at: datetime = Field(..., description="Timestamp when the quiz result was created.")


class QuizVoteRequest(BaseModel):
    """
    Model representing a request to vote on a quiz.
    """
    answers: Dict[int, int] = Field(..., description="Mapping of question IDs to answer IDs selected by the user.")


class UserQuizVote(BaseModel):
    """
    Model representing a user's vote on a quiz.
    """
    user_id: int = Field(..., description="ID of the user who voted.")
    company_id: int = Field(..., description="ID of the company.")
    quiz_id: int = Field(..., description="ID of the quiz.")
    question_id: int = Field(..., description="ID of the question.")
    question_text: str = Field(..., description="Text of the question.")
    answer_text: str = Field(..., description="Text of the answer.")
    is_correct: bool = Field(..., description="Indicates if the answer is correct.")
    timestamp: Optional[float] = Field(default_factory=time.time, description="Timestamp when the vote was recorded.")

    def to_csv_row(self):
        """
        Converts the UserQuizVote instance to a list suitable for CSV row representation.

        Returns:
            list: A list of the vote attributes.
        """
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
