from unittest.mock import patch

from app.celery import send_notifications


@patch("app.celery.check_quiz_completion")
def test_send_notifications(mock_check_quiz_completion):
    send_notifications()
    mock_check_quiz_completion.assert_called_once()
