from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Notification(Base):
    """
    Represents a notification sent to a user regarding a quiz or other event.
    """
    __tablename__ = "notifications"

    id = Column(
        Integer, primary_key=True, index=True,
        doc="The unique identifier for the notification."
    )
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False,
        doc="The ID of the user to whom the notification is sent."
    )
    quiz_id = Column(
        Integer, ForeignKey("quizzes.id"), nullable=True,
        doc="The ID of the quiz associated with the notification, if any."
    )
    message = Column(
        String, nullable=False,
        doc="The content of the notification message."
    )
    status = Column(
        String, default="unread",
        doc="The status of the notification (e.g., unread, read)."
    )
    timestamp = Column(
        DateTime, default=datetime.utcnow, nullable=False,
        doc="The timestamp when the notification was created."
    )

    user = relationship(
        "User", back_populates="notifications",
        doc="The user who received the notification."
    )
    quiz = relationship(
        "Quiz", back_populates="notifications",
        doc="The quiz associated with the notification."
    )
