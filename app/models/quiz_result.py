from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class QuizResult(Base):
    """
    Represents the result of a user's attempt at a quiz.
    """
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True, doc="The unique identifier for the quiz result.")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, doc="The ID of the user who took the quiz.")
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, doc="The ID of the quiz.")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, doc="The ID of the company associated with the quiz.")
    total_questions = Column(Integer, nullable=False, doc="The total number of questions in the quiz.")
    total_answers = Column(Integer, nullable=False, doc="The total number of answers given by the user.")
    score = Column(Float, nullable=False, doc="The score achieved by the user.")
    created_at = Column(DateTime, default=datetime.utcnow, doc="The timestamp when the quiz result was created.")

    user = relationship("User", back_populates="quiz_results", doc="The user who took the quiz.")
    quiz = relationship("Quiz", back_populates="quiz_results", doc="The quiz that was taken.")
    company = relationship("Company", back_populates="quiz_results", doc="The company associated with the quiz.")
