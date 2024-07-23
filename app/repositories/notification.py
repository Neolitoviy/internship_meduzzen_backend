from app.models.notification import Notification
from app.utils.repository import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository):
    model = Notification
