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
