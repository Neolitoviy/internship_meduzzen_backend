from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Company(Base):
    """
    Represents a company in the system.
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, doc="The unique identifier for the company.")
    name = Column(String, index=True, doc="The name of the company.")
    description = Column(String, index=True, doc="The description of the company.")
    visibility = Column(Boolean, default=True, doc="Indicates whether the company is publicly visible.")
    owner_id = Column(Integer, ForeignKey("users.id"), doc="The ID of the user who owns the company.")
    created_at = Column(DateTime, default=datetime.utcnow, doc="The time when the company was created.")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="The time when the company was last updated.")

    owner = relationship(
        "User",
        back_populates="owned_companies",
        doc="The user who owns the company."
    )
    invitations = relationship(
        "CompanyInvitation",
        back_populates="company",
        cascade="all, delete-orphan",
        doc="The list of invitations associated with the company."
    )
    members = relationship(
        "CompanyMember",
        back_populates="company",
        cascade="all, delete-orphan",
        doc="The list of members associated with the company."
    )
    requests = relationship(
        "CompanyRequest",
        back_populates="company",
        cascade="all, delete-orphan",
        doc="The list of requests associated with the company."
    )
    quizzes = relationship(
        "Quiz",
        back_populates="company",
        cascade="all, delete-orphan",
        doc="The list of quizzes associated with the company."
    )
    quiz_results = relationship(
        "QuizResult",
        back_populates="company",
        doc="The list of quiz results associated with the company."
    )
