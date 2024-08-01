from pydantic import BaseModel, Field


class AnswerSchemaCreate(BaseModel):
    """
    Schema for creating a new answer.
    """
    answer_text: str = Field(..., description="The text of the answer.")
    is_correct: bool = Field(..., description="Indicates whether the answer is correct.")

    model_config = {"from_attributes": True}


class AnswerSchemaResponse(BaseModel):
    """
    Schema for the response when retrieving an answer.
    """
    id: int = Field(..., description="The unique identifier of the answer.")
    answer_text: str = Field(..., description="The text of the answer.")
    is_correct: bool = Field(..., description="Indicates whether the answer is correct.")
    question_id: int = Field(..., description="The unique identifier of the associated question.")

    model_config = {"from_attributes": True}


class AnswerSchemaUpdate(BaseModel):
    """
    Schema for updating an existing answer.
    """
    answer_text: str = Field(..., description="The text of the answer.")
    is_correct: bool = Field(..., description="Indicates whether the answer is correct.")

    model_config = {"from_attributes": True}
