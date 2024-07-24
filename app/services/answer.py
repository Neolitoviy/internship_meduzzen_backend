from typing import List

from app.core.exceptions import AnswerNotFound, PermissionDenied, QuestionNotFound
from app.schemas.answer import (
    AnswerSchemaCreate,
    AnswerSchemaResponse,
    AnswerSchemaUpdate,
)
from app.utils.unitofwork import IUnitOfWork


class AnswerService:
    MIN_ANSWERS = 2

    @staticmethod
    async def create_answer(
        uow: IUnitOfWork,
        question_id: int,
        answer_data: AnswerSchemaCreate,
        current_user_id: int,
    ) -> AnswerSchemaResponse:
        async with uow:
            question = await uow.questions.find_one(id=question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            company = await uow.companies.find_one(id=quiz.company_id)
            if (
                company.owner_id != current_user_id
                and not await uow.company_members.find_one(
                    company_id=quiz.company_id, user_id=current_user_id, is_admin=True
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to add answers to this question."
                )

            new_answer = await uow.answers.add_one(
                {
                    "answer_text": answer_data.answer_text,
                    "is_correct": answer_data.is_correct,
                    "question_id": question_id,
                }
            )
            return AnswerSchemaResponse.model_validate(new_answer)

    @staticmethod
    async def update_answer(
        uow: IUnitOfWork,
        answer_id: int,
        answer_data: AnswerSchemaUpdate,
        current_user_id: int,
    ) -> AnswerSchemaResponse:
        async with uow:
            answer = await uow.answers.find_one(id=answer_id)
            if not answer:
                raise AnswerNotFound("Answer not found")
            question = await uow.questions.find_one(id=answer.question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            company = await uow.companies.find_one(id=quiz.company_id)
            if (
                company.owner_id != current_user_id
                and not await uow.company_members.find_one(
                    company_id=quiz.company_id, user_id=current_user_id, is_admin=True
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to update this answer"
                )

            updated_answer = await uow.answers.edit_one(
                answer_id, answer_data.model_dump(exclude_unset=True)
            )
            return AnswerSchemaResponse.model_validate(updated_answer)

    @staticmethod
    async def delete_answer(
        uow: IUnitOfWork, answer_id: int, current_user_id: int
    ) -> None:
        async with uow:
            answer = await uow.answers.find_one(id=answer_id)
            if not answer:
                raise AnswerNotFound("Answer not found")
            question = await uow.questions.find_one(id=answer.question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            company = await uow.companies.find_one(id=quiz.company_id)
            if (
                company.owner_id != current_user_id
                and not await uow.company_members.find_one(
                    company_id=quiz.company_id, user_id=current_user_id, is_admin=True
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to delete this answer"
                )
            total_answers = await uow.answers.count_all(question_id=question.id)
            if total_answers <= AnswerService.MIN_ANSWERS:
                raise PermissionDenied(
                    f"A question must have at least {AnswerService.MIN_ANSWERS} answers."
                )
            await uow.answers.delete_one(answer_id)

    @staticmethod
    async def get_answers_by_question_id(
        uow: IUnitOfWork, question_id: int, current_user_id: int, skip: int, limit: int
    ) -> List[AnswerSchemaResponse]:
        async with uow:
            question = await uow.questions.find_one(id=question_id)
            if not question:
                raise QuestionNotFound("Question not found")
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            if not quiz:
                raise PermissionDenied(
                    "Quiz not found or you do not have permission to view this quiz"
                )
            company = await uow.companies.find_one(id=quiz.company_id)
            if (
                company.owner_id != current_user_id
                and not await uow.company_members.find_one(
                    company_id=quiz.company_id, user_id=current_user_id
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to view answers for this question"
                )

            answers = await uow.answers.find_all(
                skip=skip, limit=limit, question_id=question_id
            )
            return [AnswerSchemaResponse.model_validate(answer) for answer in answers]
