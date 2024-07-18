from abc import abstractmethod, ABC
from typing import Type
from app.db.database import async_session
from app.repositories.company import CompanyRepository
from app.repositories.user import UserRepository


class IUnitOfWork(ABC):
    users: Type[UserRepository]
    companies: Type[CompanyRepository]

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session

    async def __aenter__(self):
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.companies = CompanyRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()
        if exc_type is not None:
            raise exc_val.with_traceback(exc_tb)  # With traceback

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
