from typing import Annotated

from fastapi import Depends

from app.services.answer import AnswerService
from app.services.auth import authenticate_and_get_user
from app.services.company import CompanyService
from app.services.company_invitation import CompanyInvitationService
from app.services.company_member import CompanyMemberService
from app.services.company_request import CompanyRequestService
from app.services.question import QuestionService
from app.services.quiz import QuizService
from app.services.quiz_result import QuizResultService
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork


def get_uow() -> IUnitOfWork:
    return UnitOfWork()


def get_users_service() -> UserService:
    return UserService()


def get_company_service() -> CompanyService:
    return CompanyService()


def get_company_invitation_service() -> CompanyInvitationService:
    return CompanyInvitationService()


def get_company_member_service() -> CompanyMemberService:
    return CompanyMemberService()


def get_company_request_service() -> CompanyRequestService:
    return CompanyRequestService()


def get_quiz_service() -> QuizService:
    return QuizService()


def get_question_service() -> QuestionService:
    return QuestionService()


def get_answer_service() -> AnswerService:
    return AnswerService()


def get_quiz_result_service() -> QuizResultService:
    return QuizResultService()


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]
UserServiceDep = Annotated[UserService, Depends(get_users_service)]
CurrentUserDep = Annotated[UserService, Depends(authenticate_and_get_user)]
CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]
CompanyInvitationServiceDep = Annotated[
    CompanyInvitationService, Depends(get_company_invitation_service)
]
CompanyMemberServiceDep = Annotated[
    CompanyMemberService, Depends(get_company_member_service)
]
CompanyRequestServiceDep = Annotated[
    CompanyRequestService, Depends(get_company_request_service)
]
QuizServiceDep = Annotated[QuizService, Depends(get_quiz_service)]
QuestionServiceDep = Annotated[QuestionService, Depends(get_question_service)]
AnswerServiceDep = Annotated[AnswerService, Depends(get_answer_service)]
QuizResultServiceDep = Annotated[QuizResultService, Depends(get_quiz_result_service)]
