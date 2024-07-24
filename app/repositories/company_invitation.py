from typing import List, Optional

from sqlalchemy import func, select

from app.models.company import Company
from app.models.company_invitation import CompanyInvitation
from app.utils.repository import SQLAlchemyRepository


class CompanyInvitationRepository(SQLAlchemyRepository):
    model = CompanyInvitation

    async def count_all(self, user_id: Optional[int] = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if user_id:
            stmt = stmt.where(
                (self.model.invited_user_id == user_id)
                | (
                    self.model.company_id.in_(
                        select(Company.id).where(Company.owner_id == user_id)
                    )
                )
            )
        res = await self.session.execute(stmt)
        return res.scalar()

    async def find_all(
        self, user_id: Optional[int] = None, skip: int = 0, limit: int = 10
    ) -> List[CompanyInvitation]:
        stmt = select(self.model)
        if user_id:
            stmt = stmt.where(
                (self.model.invited_user_id == user_id)
                | (
                    self.model.company_id.in_(
                        select(Company.id).where(Company.owner_id == user_id)
                    )
                )
            )
        stmt = stmt.offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()
