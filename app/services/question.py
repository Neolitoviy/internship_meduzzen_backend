from typing import List

from app.core.exceptions import PermissionDenied
from app.schemas.question import (
    QuestionSchemaCreate,
    QuestionSchemaResponse,
    UpdateQuestionRequest,
)
from app.services.company import CompanyService
from app.utils.unitofwork import IUnitOfWork


class QuestionService:
    MIN_QUESTIONS = 2

    @staticmethod
    async def create_question(
        uow: IUnitOfWork,
        quiz_id: int,
        question_data: QuestionSchemaCreate,
        current_user_id: int,
    ) -> QuestionSchemaResponse:
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )

            new_question = await uow.questions.add_one(
                {"question_text": question_data.question_text, "quiz_id": quiz_id}
            )

            for answer_data in question_data.answers:
                await uow.answers.add_one(
                    {
                        "answer_text": answer_data.answer_text,
                        "is_correct": answer_data.is_correct,
                        "question_id": new_question.id,
                    }
                )

            return QuestionSchemaResponse.model_validate(new_question)

    @staticmethod
    async def update_question(
        uow: IUnitOfWork,
        question_id: int,
        question_data: UpdateQuestionRequest,
        current_user_id: int,
    ) -> QuestionSchemaResponse:
        async with uow:
            question = await uow.questions.find_one(id=question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )

            updated_question = await uow.questions.edit_one(
                question_id, question_data.model_dump(exclude_unset=True)
            )
            return QuestionSchemaResponse.model_validate(updated_question)

    @staticmethod
    async def delete_question(
        uow: IUnitOfWork, question_id: int, current_user_id: int
    ) -> None:
        async with uow:
            question = await uow.questions.find_one(id=question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )
            await QuestionService.check_min_questions(uow, quiz.id)
            await uow.questions.delete_one(question_id)

    @staticmethod
    async def get_questions_by_quiz_id(
        uow: IUnitOfWork, quiz_id: int, current_user_id: int, skip: int, limit: int
    ) -> List[QuestionSchemaResponse]:
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id
            )

            questions = await uow.questions.find_all(
                quiz_id=quiz_id, skip=skip, limit=limit
            )
            return [
                QuestionSchemaResponse.model_validate(question)
                for question in questions
            ]

    @staticmethod
    async def check_min_questions(uow: IUnitOfWork, quiz_id: int) -> None:
        total_questions = await uow.questions.count_all(quiz_id=quiz_id)
        if total_questions <= QuestionService.MIN_QUESTIONS:
            raise PermissionDenied(
                f"A quiz must have at least {QuestionService.MIN_QUESTIONS} questions."
            )
