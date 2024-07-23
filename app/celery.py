import asyncio
import nest_asyncio
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.core.tasks import check_quiz_completion

nest_asyncio.apply()

celery = Celery("tasks", broker=settings.celery_broker_url)


@celery.task
def send_notifications():
    asyncio.run(check_quiz_completion())


celery.conf.beat_schedule = {
    'check-quiz-completion-every-day': {
        'task': 'app.celery.send_notifications',
        'schedule': crontab(hour='0', minute='0'),  # Every day at midnight
    },
}
