from pydantic import BaseModel


class AnswerSchemaCreate(BaseModel):
    answer_text: str
    is_correct: bool

    model_config = {"from_attributes": True}


class AnswerSchemaResponse(BaseModel):
    id: int
    answer_text: str
    is_correct: bool
    question_id: int

    model_config = {"from_attributes": True}


class AnswerSchemaUpdate(BaseModel):
    answer_text: str
    is_correct: bool

    model_config = {"from_attributes": True}
