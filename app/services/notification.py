from typing import List

from app.schemas.notification import NotificationResponse
from app.utils.unitofwork import IUnitOfWork


class NotificationService:
    @staticmethod
    async def get_user_notifications(
        uow: IUnitOfWork, user_id: int, skip: int, limit: int
    ) -> List[NotificationResponse]:
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
        async with uow:
            notification_data = {"status": "read"}
            updated_notification = await uow.notifications.edit_one(
                notification_id, notification_data, user_id=user_id
            )
            return NotificationResponse.model_validate(updated_notification)
