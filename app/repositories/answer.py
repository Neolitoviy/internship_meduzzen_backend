from typing import List

from sqlalchemy import select

from app.utils.repository import SQLAlchemyRepository
from app.models.answer import Answer


class AnswerRepository(SQLAlchemyRepository):
    model = Answer

    async def find_all(self, question_id: int, skip: int, limit: int) -> List[Answer]:
        stmt = select(self.model).where(self.model.question_id == question_id)
        result = await self.session.execute(stmt.offset(skip).limit(limit))
        return result.scalars().all()
