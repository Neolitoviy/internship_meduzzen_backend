from datetime import datetime
from pydantic import BaseModel


class NotificationBase(BaseModel):
    user_id: int
    quiz_id: int
    message: str


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    status: str


class NotificationResponse(NotificationBase):
    id: int
    status: str
    timestamp: datetime

    model_config = {
        'from_attributes': True
    }