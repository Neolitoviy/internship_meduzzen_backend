from abc import ABC, abstractmethod
from typing import Optional, List, Union

from sqlalchemy import RowMapping, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AddRecordError, RecordNotFound


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, skip: Optional[int], limit: Optional[int], **filter_by) -> List[RowMapping]:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, **filter_by) -> Optional[RowMapping]:
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, data: dict, **filter_by) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def delete_many(self, **filters) -> None:
        raise NotImplementedError

    @abstractmethod
    async def count_all(self, **filter_by) -> int:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> RowMapping:
        """Add a single record to the database.

        Args:
            data (dict): Data to insert.

        Returns:
            RowMapping: The newly inserted record.

        Raises:
            AddRecordError: If the record could not be added.
        """
        stmt = (
            insert(self.model).values(**data).returning(*self.model.__table__.columns)
        )
        res = await self.session.execute(stmt)
        result = res.fetchone()
        if result is None:
            raise AddRecordError("Failed to add record")
        return result._mapping

    async def edit_one(self, id: int, data: dict, **filter_by) -> RowMapping:
        """Edit a single record.

        Args:
            id (int): ID of the record to edit.
            data (dict): Data to update.
            filter_by: Additional filters to apply.

        Returns:
            RowMapping: The updated record.

        Raises:
            RecordNotFound: If the record could not be found.
        """
        stmt = (
            update(self.model)
            .values(**data)
            .filter_by(id=id, **filter_by)
            .returning(*self.model.__table__.columns)
        )
        res = await self.session.execute(stmt)
        result = res.fetchone()
        if result is None:
            raise RecordNotFound("Record not found")
        return result._mapping

    async def find_all(self, skip: Optional[int] = None, limit: Optional[int] = None, **filter_by) -> List[RowMapping]:
        """Find all records matching the given filters.

        Args:
            skip (Optional[int]): Number of records to skip.
            limit (Optional[int]): Maximum number of records to return.
            filter_by: Filters to apply.

        Returns:
            List[RowMapping]: List of records.
        """
        stmt = select(self.model).filter_by(**filter_by)
        if skip is not None:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_one(self, **filter_by) -> RowMapping:
        """Find a single record matching the given filters.

        Args:
            filter_by: Filters to apply.

        Returns:
            RowMapping: The found record.

        Raises:
            NoResultFound: If no record is found.
        """
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one()  # This will raise NoResultFound if no result

    async def find_one_or_none(self, **filter_by) -> Optional[RowMapping]:
        """Find a single record matching the given filters, or return None if no record is found.

        Args:
            filter_by: Filters to apply.

        Returns:
            Optional[RowMapping]: The found record or None.
        """
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_one(self, id: int) -> RowMapping:
        """Delete a single record.

        Args:
            id (int): ID of the record to delete.

        Returns:
            RowMapping: The deleted record.

        Raises:
            RecordNotFound: If the record could not be found.
        """
        stmt = (
            delete(self.model).filter_by(id=id).returning(*self.model.__table__.columns)
        )
        res = await self.session.execute(stmt)
        result = res.fetchone()
        if result is None:
            raise RecordNotFound("Record not found")
        return result._mapping

    async def delete_many(self, **filters) -> None:
        """Delete multiple records.

        Args:
            filters: Filters to apply to the delete operation.
        """
        stmt = delete(self.model).filter_by(**filters)
        await self.session.execute(stmt)

    async def count_all(self, **filter_by) -> int:
        """Count all records matching the given filters.

        Args:
            filter_by: Filters to apply.

        Returns:
            int: The count of records.
        """
        stmt = select(func.count()).select_from(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar()
