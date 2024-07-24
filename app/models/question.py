from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    question_text = Column(String, nullable=False)

    answers = relationship(
        "Answer", cascade="all, delete-orphan", back_populates="question"
    )
    quiz = relationship("Quiz", back_populates="questions")
