from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class CompanyMember(Base):
    """
    Represents a member of a company, which includes both regular members and admins.
    """
    __tablename__ = "company_members"

    id = Column(
        Integer, primary_key=True, index=True,
        doc="The unique identifier for the company member."
    )
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False,
        doc="The ID of the company to which the member belongs."
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        doc="The ID of the user who is a member of the company."
    )
    is_admin = Column(
        Boolean, default=False,
        doc="Indicates whether the user is an admin of the company."
    )
    created_at = Column(
        DateTime, default=datetime.utcnow,
        doc="The timestamp when the user became a member of the company."
    )

    company = relationship(
        "Company", back_populates="members",
        doc="The company to which the member belongs."
    )
    user = relationship(
        "User", back_populates="company_memberships",
        doc="The user who is a member of the company."
    )
