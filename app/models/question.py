from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Question(Base):
    """
    Represents a question in a quiz.
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, doc="The unique identifier for the question.")
    quiz_id = Column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, doc="The ID of the quiz to which the question belongs."
    )
    question_text = Column(String, nullable=False, doc="The text of the question.")

    answers = relationship(
        "Answer", cascade="all, delete-orphan", back_populates="question", doc="The list of answers for the question."
    )
    quiz = relationship("Quiz", back_populates="questions", doc="The quiz to which the question belongs.")
