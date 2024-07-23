from datetime import datetime

from sqlalchemy import select, func, desc
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

    async def get_average_score_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> float:
        stmt = select(func.avg(self.model.score)).where(
            self.model.user_id == user_id,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date
        )
        result = await self.session.execute(stmt)
        average_score = result.scalar() or 0.0
        return round(average_score, 2)

    async def find_all_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime):
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date
        ).order_by(desc(self.model.created_at))
        results = await self.session.execute(stmt)
        return results.scalars().all()
