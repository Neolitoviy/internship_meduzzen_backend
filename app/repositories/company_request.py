from sqlalchemy import select, func, Row, RowMapping
from typing import Optional, Any, Sequence

from app.models.company import Company
from app.models.company_request import CompanyRequest
from app.utils.repository import SQLAlchemyRepository


class CompanyRequestRepository(SQLAlchemyRepository):
    model = CompanyRequest

    async def count_all(self, user_id: Optional[int] = None, company_id: Optional[int] = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if user_id:
            stmt = stmt.where((self.model.requested_user_id == user_id) | (self.model.company_id.in_(select(Company.id).where(Company.owner_id == user_id))))
        res = await self.session.execute(stmt)
        return res.scalar()

    async def find_all(self, user_id: Optional[int] = None, company_id: Optional[int] = None, skip: int = 0,
                       limit: int = 10) -> Sequence[Row[Any] | RowMapping | Any]:
        stmt = select(self.model)
        if user_id:
            stmt = stmt.where((self.model.requested_user_id == user_id) | (self.model.company_id.in_(select(Company.id).where(Company.owner_id == user_id))))
        stmt = stmt.offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()
