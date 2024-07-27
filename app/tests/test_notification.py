from datetime import datetime

import pytest

from app.schemas.notification import NotificationResponse
from app.services.notification import NotificationService


@pytest.fixture
def mock_notification():
    return NotificationResponse(
        id=1,
        user_id=1,
        quiz_id=1,
        message="Test notification",
        status="unread",
        timestamp=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_get_user_notifications(uow, mock_notification):
    user_id = 1
    skip = 0
    limit = 10

    uow.notifications.find_all.return_value = [mock_notification]

    notifications = await NotificationService.get_user_notifications(
        uow, user_id, skip, limit
    )

    assert len(notifications) == 1
    assert notifications[0].id == mock_notification.id
    assert notifications[0].user_id == mock_notification.user_id
    assert notifications[0].quiz_id == mock_notification.quiz_id
    assert notifications[0].message == mock_notification.message
    assert notifications[0].status == mock_notification.status
    assert notifications[0].timestamp == mock_notification.timestamp


@pytest.mark.asyncio
async def test_mark_notification_as_read(uow, mock_notification):
    notification_id = mock_notification.id
    user_id = mock_notification.user_id

    uow.notifications.find_one.return_value = mock_notification
    mock_notification.status = "read"
    uow.notifications.edit_one.return_value = mock_notification

    updated_notification = await NotificationService.mark_notification_as_read(
        uow, notification_id, user_id
    )

    assert updated_notification.id == mock_notification.id
    assert updated_notification.user_id == mock_notification.user_id
    assert updated_notification.quiz_id == mock_notification.quiz_id
    assert updated_notification.message == mock_notification.message
    assert updated_notification.status == "read"
    assert updated_notification.timestamp == mock_notification.timestamp
