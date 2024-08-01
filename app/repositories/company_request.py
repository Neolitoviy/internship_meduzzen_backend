from typing import Any, Optional, Sequence

from sqlalchemy import Row, RowMapping, func, select

from app.models.company import Company
from app.models.company_request import CompanyRequest
from app.utils.repository import SQLAlchemyRepository


class CompanyRequestRepository(SQLAlchemyRepository):
    """
    Repository class for CompanyRequest model.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = CompanyRequest

    async def count_all(
        self, user_id: Optional[int] = None, company_id: Optional[int] = None
    ) -> int:
        """
        Count all company requests for request user or company owner.

        Args:
            user_id (Optional[int]): ID of the user.
            company_id (Optional[int]): ID of the company.

        Returns:
            int: The count of matching company requests.
        """
        stmt = select(func.count()).select_from(self.model)
        if user_id:
            stmt = stmt.where(
                (self.model.requested_user_id == user_id)
                | (
                    self.model.company_id.in_(
                        select(Company.id).where(Company.owner_id == user_id)
                    )
                )
            )
        res = await self.session.execute(stmt)
        return res.scalar()

    async def find_all(
        self,
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Find all company requests for request user or company owner.

        Args:
            user_id (Optional[int]): ID of the user.
            company_id (Optional[int]): ID of the company.
            skip (int): Number of records to skip.
            limit (int): Maximum number of records to return.

        Returns:
            Sequence[Row[Any] | RowMapping | Any]: The list of matching company requests.
        """
        stmt = select(self.model)
        if user_id:
            stmt = stmt.where(
                (self.model.requested_user_id == user_id)
                | (
                    self.model.company_id.in_(
                        select(Company.id).where(Company.owner_id == user_id)
                    )
                )
            )
        stmt = stmt.offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()
