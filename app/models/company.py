from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    visibility = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invitations = relationship(
        "CompanyInvitation", back_populates="company", cascade="all, delete-orphan"
    )
    members = relationship(
        "CompanyMember", back_populates="company", cascade="all, delete-orphan"
    )
    requests = relationship(
        "CompanyRequest", back_populates="company", cascade="all, delete-orphan"
    )
    quizzes = relationship(
        "Quiz", back_populates="company", cascade="all, delete-orphan"
    )
    quiz_results = relationship("QuizResult", back_populates="company")
