from typing import List, Optional

from sqlalchemy import func, select

from app.models.company import Company
from app.models.company_invitation import CompanyInvitation
from app.utils.repository import SQLAlchemyRepository


class CompanyInvitationRepository(SQLAlchemyRepository):
    """
    Repository class for CompanyInvitation model.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = CompanyInvitation

    async def count_all(self, user_id: Optional[int] = None) -> int:
        """
        Count the total number of company invitations for invited user or company owner.

        Args:
            user_id (Optional[int]): ID of the user to filter invitations by user ID or by the companies owned by the user.

        Returns:
            int: The total number of company invitations.
        """
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
        """
        Find all company invitations for invited user or company owner.

        Args:
            user_id (Optional[int]): ID of the user to filter invitations by user ID or by the companies owned by the user.
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.

        Returns:
            List[CompanyInvitation]: A list of company invitations.
        """
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
