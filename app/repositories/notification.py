from app.models.notification import Notification
from app.utils.repository import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository):
    """
    Repository class for Notification model.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = Notification
