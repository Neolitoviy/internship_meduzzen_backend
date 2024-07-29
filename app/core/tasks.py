from datetime import datetime

from app.schemas.notification import NotificationCreate
from app.utils.unitofwork import UnitOfWork


async def check_quiz_completion():
    async with UnitOfWork() as uow:
        company_members = await uow.company_members.find_abs_all()
        for member in company_members:
            last_attempt = await uow.quiz_results.find_last_attempt_with_filter(
                user_id=member.user_id
            )
            quiz = await uow.quizzes.find_one(id=last_attempt.quiz_id)
            time_passed = (datetime.utcnow() - last_attempt.created_at).days
            if time_passed >= quiz.frequency_in_days:
                notification = NotificationCreate(
                    user_id=member.user_id,
                    quiz_id=quiz.id,
                    message=f"You should complete the quiz '{quiz.title}' again!",
                )
                await uow.notifications.add_one(notification.model_dump())
