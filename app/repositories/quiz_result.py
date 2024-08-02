from datetime import datetime

from sqlalchemy import desc, func, select

from app.models import CompanyMember
from app.models.quiz_result import QuizResult
from app.utils.repository import SQLAlchemyRepository


class QuizResultRepository(SQLAlchemyRepository):
    """
    Repository class for handling quiz result-related operations.

    Inherits from:
        SQLAlchemyRepository: Base class for SQLAlchemy operations.

    Attributes:
        model: The SQLAlchemy model class associated with this repository.
    """
    model = QuizResult

    async def get_average_score(self, **filter_by) -> float:
        """
        Calculate the average score of quiz results based on provided filters.

        Args:
            **filter_by: Arbitrary keyword arguments for filtering quiz results.

        Returns:
            float: The average score of the filtered quiz results, rounded to 2 decimal places.
        """
        stmt = select(func.avg(self.model.score)).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        average_score = result.scalar() or 0.0
        return round(average_score, 2)

    async def find_last_attempt_with_filter(self, **filter_by) -> QuizResult:
        """
        Find the most recent quiz result based on provided filters.

        Args:
            **filter_by: Arbitrary keyword arguments for filtering quiz results.

        Returns:
            QuizResult: The most recent quiz result that matches the filters.
        """
        stmt = (
            select(QuizResult)
            .filter_by(**filter_by)
            .order_by(desc(self.model.created_at))
            .limit(1)
        )
        results = await self.session.execute(stmt)
        return results.scalars().first()

    async def get_company_members_average_scores(
        self,
        company_id: int,
        start_date: datetime,
        end_date: datetime,
        skip: int,
        limit: int,
    ):
        """
        Calculate the average scores of company members within a date range.

        Args:
            company_id (int): The ID of the company.
            start_date (datetime): The start date of the range.
            end_date (datetime): The end date of the range.
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.

        Returns:
            List[Tuple]: A list of tuples containing user ID, average score, start date, and end date.
        """
        stmt = (
            select(
                QuizResult.user_id,
                func.avg(QuizResult.score).label("average_score"),
                func.min(QuizResult.created_at).label("start_date"),
                func.max(QuizResult.created_at).label("end_date"),
            )
            .join(CompanyMember, self.model.user_id == CompanyMember.user_id)
            .where(CompanyMember.company_id == company_id)
            .where(QuizResult.created_at >= start_date)
            .where(QuizResult.created_at <= end_date)
            .group_by(QuizResult.user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.fetchall()

    async def get_quiz_trends_by_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        skip: int,
        limit: int,
    ):
        """
        Calculate the trends of quiz scores for a user within a date range.

        Args:
            user_id (int): The ID of the user.
            start_date (datetime): The start date of the range.
            end_date (datetime): The end date of the range.
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.

        Returns:
            List[Tuple]: A list of tuples containing quiz ID, average score, start date, end date, and count.
        """
        stmt = (
            select(
                self.model.quiz_id,
                func.avg(self.model.score).label("average_score"),
                func.min(self.model.created_at).label("start_date"),
                func.max(self.model.created_at).label("end_date"),
                func.count(self.model.id).label("count"),
            )
            .where(self.model.user_id == user_id)
            .where(self.model.created_at >= start_date)
            .where(self.model.created_at <= end_date)
            .group_by(self.model.quiz_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.fetchall()
