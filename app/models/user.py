from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    city = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owned_companies = relationship("Company", back_populates="owner")
    company_invitations_received = relationship(
        "CompanyInvitation",
        foreign_keys="[CompanyInvitation.invited_user_id]",
        back_populates="invited_user",
    )
    company_memberships = relationship("CompanyMember", back_populates="user")
    company_requests = relationship("CompanyRequest", back_populates="requested_user")
    quizzes = relationship("Quiz", back_populates="user")
    quiz_results = relationship("QuizResult", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
