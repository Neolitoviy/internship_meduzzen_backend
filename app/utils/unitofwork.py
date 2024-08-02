from abc import ABC, abstractmethod

from app.db.database import async_session
from app.repositories.answer import AnswerRepository
from app.repositories.company import CompanyRepository
from app.repositories.company_invitation import CompanyInvitationRepository
from app.repositories.company_member import CompanyMemberRepository
from app.repositories.company_request import CompanyRequestRepository
from app.repositories.notification import NotificationRepository
from app.repositories.question import QuestionRepository
from app.repositories.quiz import QuizRepository
from app.repositories.quiz_result import QuizResultRepository
from app.repositories.user import UserRepository


class IUnitOfWork(ABC):
    """
    Interface for UnitOfWork pattern, which ensures atomicity of database operations.
    This interface is designed to handle multiple repositories in a single transaction.
    """
    users: UserRepository
    companies: CompanyRepository
    company_invitations: CompanyInvitationRepository
    company_members: CompanyMemberRepository
    company_requests: CompanyRequestRepository
    quizzes: QuizRepository
    questions: QuestionRepository
    answers: AnswerRepository
    quiz_results: QuizResultRepository
    notifications: NotificationRepository

    @abstractmethod
    def __init__(self):
        """
        Initialize the UnitOfWork.
        """
        pass

    @abstractmethod
    async def __aenter__(self):
        """
        Enter the runtime context related to this object.
        This method is called when the execution flow enters the context of the 'async with' statement.
        """
        pass

    @abstractmethod
    async def __aexit__(self, *args):
        """
        Exit the runtime context related to this object.
        This method is called when the execution flow leaves the context of the 'async with' statement.
        """
        pass

    @abstractmethod
    async def commit(self):
        """
        Commit the transaction.
        This method is used to save the changes made during the UnitOfWork.
        """
        pass

    @abstractmethod
    async def rollback(self):
        """
        Rollback the transaction.
        This method is used to undo the changes made during the UnitOfWork in case of an error.
        """
        pass


class UnitOfWork(IUnitOfWork):
    """
    Concrete implementation of the UnitOfWork interface.
    Manages database transactions and ensures all changes are committed or rolled back atomically.
    """
    def __init__(self):
        """
        Initialize the UnitOfWork with an asynchronous session factory.
        """
        self.session_factory = async_session

    async def __aenter__(self):
        """
        Initialize the asynchronous database session and repositories.
        Called when entering the 'async with' context.
        """
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.companies = CompanyRepository(self.session)
        self.company_invitations = CompanyInvitationRepository(self.session)
        self.company_members = CompanyMemberRepository(self.session)
        self.company_requests = CompanyRequestRepository(self.session)
        self.quizzes = QuizRepository(self.session)
        self.questions = QuestionRepository(self.session)
        self.answers = AnswerRepository(self.session)
        self.quiz_results = QuizResultRepository(self.session)
        self.notifications = NotificationRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Commit or rollback the transaction based on whether an exception occurred.
        Close the asynchronous database session.
        """
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()
        if exc_type is not None:
            raise exc_val.with_traceback(exc_tb)  # Re-raise the exception with traceback

    async def commit(self):
        """
        Commit the transaction.
        Save all changes made during the UnitOfWork.
        This is an asynchronous operation.
        """
        await self.session.commit()

    async def rollback(self):
        """
        Rollback the transaction.
        Undo all changes made during the UnitOfWork.
        This is an asynchronous operation.
        """
        await self.session.rollback()
