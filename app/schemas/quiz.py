from typing import List, Optional

from pydantic import BaseModel, conlist, Field

from app.schemas.question import QuestionSchemaCreate
from app.utils.pagination import PaginationResponse


class CreateQuizRequest(BaseModel):
    """
    Schema for creating a new quiz.
    """
    title: str = Field(..., description="Title of the quiz.")
    description: Optional[str] = Field(None, description="Description of the quiz.")
    frequency_in_days: int = Field(..., description="Frequency of the quiz in days.")
    questions_data: conlist(QuestionSchemaCreate, min_length=2) = Field(..., description="List of questions for the quiz. Minimum items equals 2.")
    company_id: int = Field(..., description="ID of the company creating the quiz.")

    model_config = {"from_attributes": True}


class QuizSchemaResponse(BaseModel):
    """
    Schema for the quiz response.
    """
    id: int = Field(..., description="Unique identifier of the quiz.")
    title: str = Field(..., description="Title of the quiz.")
    description: Optional[str] = Field(None, description="Description of the quiz.")
    frequency_in_days: int = Field(..., description="Frequency of the quiz in days.")
    company_id: int = Field(..., description="ID of the company that created the quiz.")
    user_id: int = Field(..., description="ID of the user who created the quiz.")

    model_config = {"from_attributes": True}


class QuizzesListResponse(PaginationResponse):
    """
    Schema for paginated response of quizzes.
    """
    items: List[QuizSchemaResponse] = Field(..., description="List of quizzes.")

    model_config = {"from_attributes": True}


class UpdateQuizRequest(BaseModel):
    """
    Schema for updating an existing quiz.
    """
    title: str = Field(..., description="Updated title of the quiz.")
    description: str = Field(..., description="Updated description of the quiz.")
    frequency_in_days: int = Field(..., description="Updated frequency of the quiz in days.")

    model_config = {"from_attributes": True}
