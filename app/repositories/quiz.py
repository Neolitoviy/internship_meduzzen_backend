from typing import List

from sqlalchemy import select, func

from app.models.quiz import Quiz
from app.utils.repository import SQLAlchemyRepository


class QuizRepository(SQLAlchemyRepository):
    model = Quiz

    async def find_all(self, company_id: int, skip: int, limit: int) -> List[Quiz]:
        stmt = select(self.model).where(self.model.company_id == company_id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_all(self, company_id: int) -> int:
        stmt = select(func.count()).select_from(self.model).where(self.model.company_id == company_id)
        result = await self.session.execute(stmt)
        return result.scalar()
