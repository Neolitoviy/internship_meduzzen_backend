from datetime import datetime

from app.schemas.quiz_result import QuizResultResponse, QuizVoteRequest
from app.services.company import CompanyService
from app.utils.unitofwork import IUnitOfWork


class QuizResultService:
    @staticmethod
    async def quiz_vote(
        uow: IUnitOfWork,
        company_id: int,
        quiz_id: int,
        vote_data: QuizVoteRequest,
        user_id: int,
    ) -> QuizResultResponse:
        async with uow:
            await CompanyService.check_company_permission(uow, company_id, user_id)
            total_questions = 0
            total_answers = 0
            for question_id, answer_id in vote_data.answers.items():
                await uow.questions.find_one(id=question_id, quiz_id=quiz_id)
                answer = await uow.answers.find_one(
                    id=answer_id, question_id=question_id
                )
                if answer.is_correct:
                    total_answers += 1
                total_questions += 1

            quiz_result = await uow.quiz_results.add_one(
                {
                    "user_id": user_id,
                    "quiz_id": quiz_id,
                    "company_id": company_id,
                    "total_questions": total_questions,
                    "total_answers": total_answers,
                    "score": round((total_answers / total_questions) * 100, 2),
                    "created_at": datetime.utcnow(),
                }
            )
            return QuizResultResponse.model_validate(quiz_result)

    @staticmethod
    async def get_user_average_score(uow: IUnitOfWork, user_id: int) -> float:
        async with uow:
            return await uow.quiz_results.get_average_score(user_id=user_id)

    @staticmethod
    async def get_company_average_score(
        uow: IUnitOfWork, company_id: int, user_id: int
    ) -> float:
        async with uow:
            await CompanyService.check_company_permission(uow, company_id, user_id)
            return await uow.quiz_results.get_average_score(company_id=company_id)
