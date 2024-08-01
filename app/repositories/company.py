from sqlalchemy import func, or_, select

from app.models.company import Company
from app.utils.repository import SQLAlchemyRepository


class CompanyRepository(SQLAlchemyRepository):
    """
    Repository class for Company model.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = Company

    async def find_visible_companies(self, skip: int, limit: int, user_id: int):
        """
        Find companies that are visible to a user.

        Args:
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.
            user_id (int): ID of the user.

        Returns:
            List[Company]: A list of visible companies.
        """
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
        """
        Count the number of companies visible to a user.

        Args:
            user_id (int): ID of the user.

        Returns:
            int: The number of visible companies.
        """
        stmt = select(func.count()).where(
            or_(self.model.owner_id == user_id, self.model.visibility.is_(True))
        )
        res = await self.session.execute(stmt)
        return res.scalar()
