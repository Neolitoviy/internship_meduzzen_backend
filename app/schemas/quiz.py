from typing import List, Optional

from pydantic import BaseModel, conlist

from app.schemas.question import QuestionSchemaCreate


class CreateQuizRequest(BaseModel):
    title: str
    description: Optional[str]
    frequency_in_days: int
    questions_data: conlist(QuestionSchemaCreate, min_length=2)
    company_id: int

    model_config = {"from_attributes": True}


class QuizSchemaResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    frequency_in_days: int
    company_id: int
    user_id: int

    model_config = {"from_attributes": True}


class PaginationLinks(BaseModel):
    previous: Optional[str]
    next: Optional[str]


class QuizzesListResponse(BaseModel):
    total_item: int
    total_page: int
    current_page: int
    pagination: PaginationLinks
    data: List[QuizSchemaResponse]

    model_config = {"from_attributes": True}


class UpdateQuizRequest(BaseModel):
    title: str
    description: str
    frequency_in_days: int

    model_config = {"from_attributes": True}
