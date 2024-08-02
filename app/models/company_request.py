from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class CompanyRequest(Base):
    """
    Represents a request made by a user to join a company.
    """
    __tablename__ = "company_requests"

    id = Column(
        Integer, primary_key=True, index=True,
        doc="The unique identifier for the company request."
    )
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False,
        doc="The ID of the company to which the request is made."
    )
    requested_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        doc="The ID of the user making the request."
    )
    status = Column(
        String, nullable=True, default="pending",
        doc="The status of the request (e.g., pending, accepted, declined)."
    )
    created_at = Column(
        DateTime, default=datetime.utcnow,
        doc="The timestamp when the request was created."
    )

    company = relationship(
        "Company", back_populates="requests",
        doc="The company to which the request is made."
    )
    requested_user = relationship(
        "User", back_populates="company_requests",
        doc="The user making the request."
    )
