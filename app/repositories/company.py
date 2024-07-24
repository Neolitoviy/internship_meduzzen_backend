from sqlalchemy import func, or_, select

from app.models.company import Company
from app.utils.repository import SQLAlchemyRepository


class CompanyRepository(SQLAlchemyRepository):
    model = Company

    async def find_visible_companies(self, skip: int, limit: int, user_id: int):
        stmt = (
            select(self.model)
            .where(
                or_(
                    self.model.owner_id == user_id,
                    self.model.visibility.is_(True),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_visible_companies(self, user_id: int) -> int:
        stmt = select(func.count()).where(
            or_(self.model.owner_id == user_id, self.model.visibility.is_(True))
        )
        res = await self.session.execute(stmt)
        return res.scalar()
