from datetime import datetime

from app.schemas.notification import NotificationCreate
from app.utils.unitofwork import UnitOfWork


async def check_quiz_completion():
    """
    Check for quizzes that need to be completed again based on their frequency
    and notify the respective company members.

    This function is designed to be used as a Celery task, which can be scheduled
    to run periodically.

    The function performs the following steps:
    1. Fetches all company members.
    2. For each member, finds their last quiz attempt.
    3. Determines if the time since the last attempt exceeds the quiz frequency.
    4. Sends a notification to the member if the quiz needs to be completed again.

    Raises:
        HTTPException: If any errors occur during the process.
    """
    async with UnitOfWork() as uow:
        company_members = await uow.company_members.find_abs_all()
        for member in company_members:
            last_attempt = await uow.quiz_results.find_last_attempt_with_filter(
                user_id=member.user_id
            )
            quiz = await uow.quizzes.find_one(id=last_attempt.quiz_id)
            time_passed = (datetime.utcnow() - last_attempt.created_at).days
            if time_passed <= quiz.frequency_in_days:
                notification = NotificationCreate(
                    user_id=member.user_id,
                    quiz_id=quiz.id,
                    message=f"You should complete the quiz '{quiz.title}' again!",
                )
                await uow.notifications.add_one(notification.model_dump())
