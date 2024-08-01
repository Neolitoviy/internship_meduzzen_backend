from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class CompanyInvitation(Base):
    """
    Represents an invitation for a user to join a company.
    """
    __tablename__ = "company_invitations"

    id = Column(
        Integer, primary_key=True, index=True,
        doc="The unique identifier for the company invitation."
    )
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False,
        doc="The ID of the company that sent the invitation."
    )
    invited_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        doc="The ID of the user who is invited to join the company."
    )
    status = Column(
        String, nullable=True, default="pending",
        doc="The status of the invitation (e.g., 'pending', 'accepted', 'declined')."
    )
    created_at = Column(
        DateTime, default=datetime.utcnow,
        doc="The timestamp when the invitation was created."
    )

    company = relationship(
        "Company", back_populates="invitations",
        doc="The company that sent the invitation."
    )
    invited_user = relationship(
        "User", foreign_keys=[invited_user_id],
        doc="The user who is invited to join the company."
    )
