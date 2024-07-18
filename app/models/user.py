from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from datetime import datetime

from sqlalchemy.orm import relationship
from app.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    city = Column(String)
    phone = Column(String)
    avatar = Column(String)
    hashed_password = Column(String, nullable=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now(), nullable=False)
    companies = relationship("Company", back_populates="owner")
