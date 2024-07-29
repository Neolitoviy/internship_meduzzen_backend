import asyncio

import nest_asyncio
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.tasks import check_quiz_completion

nest_asyncio.apply()

celery = Celery(
    "tasks", broker=f"rediss://{settings.redis_host}:{settings.redis_port}/0"
)

celery.conf.update(
    broker_use_ssl={
        'ssl_cert_reqs': None  # This disables SSL certificate verification
    }
)


@celery.task
def send_notifications():
    asyncio.run(check_quiz_completion())


celery.conf.beat_schedule = {
    "check-quiz-completion-every-day": {
        "task": "app.celery.send_notifications",
        "schedule": crontab(minute="*"),  # Every minute
    },
}
