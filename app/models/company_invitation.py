from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class CompanyInvitation(Base):
    __tablename__ = "company_invitations"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    invited_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=True, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="invitations")
    invited_user = relationship("User", foreign_keys=[invited_user_id])
