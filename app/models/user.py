from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    """
    Represents a user in the system.

    This model includes basic user information and relationships with other entities in the system.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, doc="The unique identifier for the user.")
    email = Column(String, unique=True, index=True, nullable=False, doc="The email address of the user.")
    is_active = Column(Boolean, default=True, doc="Indicates whether the user is active.")
    firstname = Column(String, nullable=True, doc="The first name of the user.")
    lastname = Column(String, nullable=True, doc="The last name of the user.")
    city = Column(String, nullable=True, doc="The city where the user lives.")
    phone = Column(String, nullable=True, doc="The phone number of the user.")
    avatar = Column(String, nullable=True, doc="The URL of the user's avatar.")
    hashed_password = Column(String, nullable=True, doc="The hashed password of the user.")
    is_superuser = Column(Boolean, default=False, doc="Indicates whether the user has superuser privileges.")
    created_at = Column(DateTime, default=datetime.utcnow, doc="The time when the user was created.")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="The time when the user was last updated.")

    owned_companies = relationship(
        "Company",
        back_populates="owner",
        doc="The list of companies owned by the user."
    )
    company_invitations_received = relationship(
        "CompanyInvitation",
        foreign_keys="[CompanyInvitation.invited_user_id]",
        back_populates="invited_user",
        doc="The list of company invitations received by the user."
    )
    company_memberships = relationship(
        "CompanyMember",
        back_populates="user",
        doc="The list of company memberships of the user."
    )
    company_requests = relationship(
        "CompanyRequest",
        back_populates="requested_user",
        doc="The list of company join requests made by the user."
    )
    quizzes = relationship(
        "Quiz",
        back_populates="user",
        doc="The list of quizzes created by the user."
    )
    quiz_results = relationship(
        "QuizResult",
        back_populates="user",
        doc="The list of quiz results for the user."
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        doc="The list of notifications received by the user."
    )
