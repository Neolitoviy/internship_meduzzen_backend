from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Quiz(Base):
    """
    Represents a quiz in the system.
    """
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True, doc="The unique identifier for the quiz.")
    title = Column(String, nullable=False, doc="The title of the quiz.")
    description = Column(String, nullable=True, doc="The description of the quiz.")
    frequency_in_days = Column(Integer, nullable=False, doc="The frequency in days with which the quiz should be taken.")
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, doc="The ID of the company to which the quiz belongs."
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, doc="The ID of the user who created the quiz."
    )
    created_at = Column(DateTime, default=datetime.utcnow, doc="The time when the quiz was created.")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="The time when the quiz was last updated.")

    questions = relationship(
        "Question", cascade="all, delete-orphan", back_populates="quiz", doc="The list of questions in the quiz."
    )
    company = relationship("Company", back_populates="quizzes", doc="The company to which the quiz belongs.")
    user = relationship("User", back_populates="quizzes", doc="The user who created the quiz.")
    quiz_results = relationship("QuizResult", back_populates="quiz", doc="The list of results for the quiz.")
    notifications = relationship("Notification", back_populates="quiz", doc="The list of notifications for the quiz.")
