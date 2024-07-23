from datetime import datetime

from sqlalchemy import select, func, desc

from app.models import CompanyMember
from app.models.quiz_result import QuizResult
from app.utils.repository import SQLAlchemyRepository


class QuizResultRepository(SQLAlchemyRepository):
    model = QuizResult

    async def get_average_score(self, **filter_by) -> float:
        stmt = select(func.avg(self.model.score)).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        average_score = result.scalar() or 0.0
        return round(average_score, 2)

    async def find_last_attempt_with_filter(self, **filter_by) -> QuizResult:
        stmt = (
            select(QuizResult)
            .filter_by(**filter_by)
            .order_by(desc(QuizResult.created_at))
            .limit(1)
        )
        results = await self.session.execute(stmt)
        return results.scalars().first()

    async def get_company_members_average_scores(self, company_id: int, start_date: datetime, end_date: datetime,
                                                 skip: int, limit: int):
        stmt = (
            select(
                QuizResult.user_id,
                func.avg(QuizResult.score).label("average_score"),
                func.min(QuizResult.created_at).label("start_date"),
                func.max(QuizResult.created_at).label("end_date")
            )
            .join(CompanyMember, QuizResult.user_id == CompanyMember.user_id)
            .where(CompanyMember.company_id == company_id)
            .where(QuizResult.created_at >= start_date)
            .where(QuizResult.created_at <= end_date)
            .group_by(QuizResult.user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.fetchall()

    async def get_quiz_trends_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime, skip: int, limit: int):
        stmt = (
            select(
                self.model.quiz_id,
                func.avg(self.model.score).label("average_score"),
                func.min(self.model.created_at).label("start_date"),
                func.max(self.model.created_at).label("end_date"),
                func.count(self.model.id).label("count")
            )
            .where(self.model.user_id == user_id)
            .where(self.model.created_at >= start_date)
            .where(self.model.created_at <= end_date)
            .group_by(self.model.quiz_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.fetchall()
