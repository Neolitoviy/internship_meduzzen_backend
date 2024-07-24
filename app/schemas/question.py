from typing import List

from pydantic import BaseModel, conlist

from app.schemas.answer import AnswerSchemaCreate, AnswerSchemaResponse


class QuestionSchemaCreate(BaseModel):
    question_text: str
    answers: conlist(AnswerSchemaCreate, min_length=2)

    model_config = {"from_attributes": True}


class QuestionSchemaResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str

    model_config = {"from_attributes": True}


class UpdateQuestionRequest(BaseModel):
    question_text: str

    model_config = {"from_attributes": True}
