from typing import List

from sqlalchemy import select

from app.utils.repository import SQLAlchemyRepository
from app.models.question import Question


class QuestionRepository(SQLAlchemyRepository):
    model = Question

    async def find_all(self, quiz_id: int) -> List[Question]:
        stmt = select(self.model).where(self.model.quiz_id == quiz_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()