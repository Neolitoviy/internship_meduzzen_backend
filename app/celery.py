import asyncio

import nest_asyncio
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.tasks import check_quiz_completion

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Initialize Celery
celery = Celery(
    "tasks", broker=f"redis://{settings.redis_host}:{settings.redis_port}/0"
)


@celery.task
def send_notifications():
    """
    Celery task to check quiz completion and send notifications.

    This task runs the check_quiz_completion function using asyncio.
    """
    asyncio.run(check_quiz_completion())


# Configure the Celery beat schedule
celery.conf.beat_schedule = {
    "check-quiz-completion-every-day": {
        "task": "app.celery.send_notifications",
        "schedule": crontab(hour="0", minute="0"),  # Every day at midnight
    },
}
