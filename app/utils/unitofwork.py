from abc import abstractmethod, ABC
from app.db.database import async_session
from app.repositories.answer import AnswerRepository
from app.repositories.company import CompanyRepository
from app.repositories.company_invitation import CompanyInvitationRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.company_request import CompanyRequestRepository
from app.repositories.question import QuestionRepository
from app.repositories.quiz import QuizRepository
from app.repositories.user import UserRepository


class IUnitOfWork(ABC):
    users: UserRepository
    companies: CompanyRepository
    company_invitations: CompanyInvitationRepository
    company_members: CompanyMemberRepository
    company_requests: CompanyRequestRepository
    users: Type[UserRepository]
    companies: Type[CompanyRepository]
    company_invitations: Type[CompanyInvitationRepository]
    company_members: Type[CompanyMemberRepository]
    company_requests: Type[CompanyRequestRepository]
    quizzes: Type[QuizRepository]
    questions: Type[QuestionRepository]
    answers: Type[AnswerRepository]

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
        self.company_invitations = CompanyInvitationRepository(self.session)
        self.company_members = CompanyMemberRepository(self.session)
        self.company_requests = CompanyRequestRepository(self.session)
        self.quizzes = QuizRepository(self.session)
        self.questions = QuestionRepository(self.session)
        self.answers = AnswerRepository(self.session)
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