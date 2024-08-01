from pydantic import BaseModel, conlist, Field

from app.schemas.answer import AnswerSchemaCreate


class QuestionSchemaCreate(BaseModel):
    """
    Schema for creating a new question.
    """
    question_text: str = Field(..., description="The text of the question.")
    answers: conlist(AnswerSchemaCreate, min_length=2) = Field(..., description="A list of answers for the question, a minimum of 2 answers.")

    model_config = {"from_attributes": True}


class QuestionSchemaResponse(BaseModel):
    """
    Schema for the response when retrieving a question.
    """
    id: int = Field(..., description="The unique identifier of the question.")
    quiz_id: int = Field(..., description="The unique identifier of the quiz to which the question belongs.")
    question_text: str = Field(..., description="The text of the question.")

    model_config = {"from_attributes": True}


class UpdateQuestionRequest(BaseModel):
    """
    Schema for updating an existing question.
    """
    question_text: str = Field(..., description="The updated text of the question.")

    model_config = {"from_attributes": True}
