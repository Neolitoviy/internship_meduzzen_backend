from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from faker import Faker

from app.utils.unitofwork import UnitOfWork

faker = Faker()


@pytest_asyncio.fixture
async def uow():
    uow = AsyncMock(UnitOfWork)
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    uow.users = AsyncMock()
    uow.companies = AsyncMock()
    uow.company_members = AsyncMock()
    uow.company_invitations = AsyncMock()
    uow.company_requests = AsyncMock()
    uow.quizzes = AsyncMock()
    uow.questions = AsyncMock()
    uow.answers = AsyncMock()
    uow.quiz_results = AsyncMock()
    uow.notifications = AsyncMock()
    return uow


@pytest.fixture
def mock_redis_client():
    client = AsyncMock()
    return client
