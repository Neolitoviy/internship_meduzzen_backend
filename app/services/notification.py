from typing import List

from app.schemas.notification import NotificationResponse
from app.utils.unitofwork import IUnitOfWork


class NotificationService:
    """
    A service class for handling notifications.

    """
    @staticmethod
    async def get_user_notifications(
        uow: IUnitOfWork, user_id: int, skip: int, limit: int
    ) -> List[NotificationResponse]:
        """
        Retrieves a paginated list of notifications for a specific user.

        Args:
            uow (IUnitOfWork): The unit of work to use for database operations.
            user_id (int): The ID of the user whose notifications are to be retrieved.
            skip (int): The number of records to skip for pagination.
            limit (int): The maximum number of records to return for pagination.

        Returns:
            List[NotificationResponse]: A list of notifications for the user.
        """
        async with uow:
            notifications = await uow.notifications.find_all(
                skip=skip, limit=limit, user_id=user_id
            )
            return [
                NotificationResponse.model_validate(notification)
                for notification in notifications
            ]

    @staticmethod
    async def mark_notification_as_read(
        uow: IUnitOfWork, notification_id: int, user_id: int
    ) -> NotificationResponse:
        """
        Marks a specific notification as "read" for a user.

        Args:
            uow (IUnitOfWork): The unit of work to use for database operations.
            notification_id (int): The ID of the notification to be marked as read.
            user_id (int): The ID of the user marking the notification as read, always current user.

        Returns:
            NotificationResponse: The updated notification with status marked as read.
        """
        async with uow:
            notification_data = {"status": "read"}
            updated_notification = await uow.notifications.edit_one(
                notification_id, notification_data, user_id=user_id
            )
            return NotificationResponse.model_validate(updated_notification)
