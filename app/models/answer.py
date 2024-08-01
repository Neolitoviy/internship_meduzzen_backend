from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Answer(Base):
    """
    Represents an answer to a question in a quiz.
    """
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True, doc="The unique identifier for the answer.")
    question_id = Column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, doc="The ID of the question to which the answer belongs."
    )
    answer_text = Column(String, nullable=False, doc="The text of the answer.")
    is_correct = Column(Boolean, default=False, doc="Indicates whether the answer is correct.")

    question = relationship("Question", back_populates="answers", doc="The question to which the answer belongs.")
