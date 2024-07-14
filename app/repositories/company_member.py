from sqlalchemy import select, func
from typing import List, Optional

from sqlalchemy.orm import joinedload

from app.models.company_member import CompanyMember
from app.utils.repository import SQLAlchemyRepository


class CompanyMemberRepository(SQLAlchemyRepository):
    model = CompanyMember

    async def count_all(self, company_id: Optional[int] = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if company_id:
            stmt = stmt.where(self.model.company_id == company_id)
        res = await self.session.execute(stmt)
        return res.scalar()

    async def find_all(self, company_id: Optional[int] = None, skip: int = 0, limit: int = 10) -> List[CompanyMember]:
        stmt = select(self.model)
        if company_id:
            stmt = stmt.where(self.model.company_id == company_id)
        stmt = stmt.offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_admins(self, company_id: int) -> int:
        stmt = select(func.count()).where(
            self.model.company_id == company_id,
            self.model.is_admin == True
        )
        res = await self.session.execute(stmt)
        return res.scalar()

    async def find_admins(self, company_id: int, skip: int = 0, limit: int = 10) -> List[CompanyMember]:
        stmt = select(self.model).options(joinedload(self.model.company)).where(
            self.model.company_id == company_id,
            self.model.is_admin == True
        ).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()


