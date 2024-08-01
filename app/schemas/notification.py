from datetime import datetime

from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    """
    Base schema for notifications.
    """
    user_id: int = Field(..., description="The ID of the user associated with the notification.")
    quiz_id: int = Field(..., description="The ID of the quiz associated with the notification.")
    message: str = Field(..., description="The message content of the notification.")


class NotificationCreate(NotificationBase):
    """
    Schema for creating a new notification.
    Inherits from NotificationBase.
    """
    pass


class NotificationUpdate(BaseModel):
    """
    Schema for updating an existing notification.
    """
    status: str = Field(..., description="The new status of the notification (e.g., 'read').")


class NotificationResponse(NotificationBase):
    """
    Schema for returning notification data to the client.
    Inherits from NotificationBase.
    """
    id: int = Field(..., description="The ID of the notification.")
    status: str = Field(..., description="The status of the notification (e.g., 'read' or 'unread').")
    timestamp: datetime = Field(..., description="The timestamp when the notification was created.")

    model_config = {"from_attributes": True}
