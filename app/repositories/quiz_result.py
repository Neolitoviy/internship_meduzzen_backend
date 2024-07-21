from sqlalchemy import select, func
from app.models.quiz_result import QuizResult
from app.utils.repository import SQLAlchemyRepository


class QuizResultRepository(SQLAlchemyRepository):
    model = QuizResult

    async def get_average_score(self, **filter_by) -> float:
        stmt = select(func.avg(self.model.score)).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        average_score = result.scalar() or 0.0
        return round(average_score, 2)

    async def find_last_attempt(self, user_id: int) -> QuizResult:
        stmt = select(QuizResult).where(QuizResult.user_id == user_id).order_by(QuizResult.created_at.desc()).limit(1)
        results = await self.session.execute(stmt)
        return results.scalars().first()
