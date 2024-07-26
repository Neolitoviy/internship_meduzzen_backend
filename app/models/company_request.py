from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class CompanyRequest(Base):
    __tablename__ = "company_requests"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    requested_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String, nullable=True, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="requests")
    requested_user = relationship("User", back_populates="company_requests")
