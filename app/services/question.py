from typing import List

from app.utils.unitofwork import IUnitOfWork
from app.schemas.question import QuestionSchemaCreate, QuestionSchemaResponse, UpdateQuestionRequest
from app.core.exceptions import QuestionNotFound, PermissionDenied, QuizNotFound


class QuestionService:
    MIN_QUESTIONS = 2

    @staticmethod
    async def create_question(uow: IUnitOfWork, quiz_id: int, question_data: QuestionSchemaCreate,
                              current_user_id: int) -> QuestionSchemaResponse:
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            company = await uow.companies.find_one(id=quiz.company_id)
            if company.owner_id != current_user_id and not await uow.company_members.find_one(
                    company_id=quiz.company_id, user_id=current_user_id, is_admin=True):
                raise PermissionDenied("You do not have permission to add questions to this quiz.")

            new_question = await uow.questions.add_one({
                'question_text': question_data.question_text,
                'quiz_id': quiz_id
            })

            for answer_data in question_data.answers:
                await uow.answers.add_one({
                    'answer_text': answer_data.answer_text,
                    'is_correct': answer_data.is_correct,
                    'question_id': new_question.id
                })

            return QuestionSchemaResponse.model_validate(new_question)

    @staticmethod
    async def update_question(uow: IUnitOfWork, question_id: int, question_data: UpdateQuestionRequest,
                              current_user_id: int) -> QuestionSchemaResponse:
        async with uow:
            question = await uow.questions.find_one(id=question_id)
            if not question:
                raise QuestionNotFound("Question not found")
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            company = await uow.companies.find_one(id=quiz.company_id)
            if company.owner_id != current_user_id and not await uow.company_members.find_one(
                    company_id=quiz.company_id, user_id=current_user_id, is_admin=True):
                raise PermissionDenied("You do not have permission to update this question")

            updated_question = await uow.questions.edit_one(question_id, question_data.model_dump(exclude_unset=True))
            return QuestionSchemaResponse.model_validate(updated_question)

    @staticmethod
    async def delete_question(uow: IUnitOfWork, question_id: int, current_user_id: int) -> None:
        async with uow:
            question = await uow.questions.find_one(id=question_id)
            if not question:
                raise QuestionNotFound("Question not found")
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            company = await uow.companies.find_one(id=quiz.company_id)
            if company.owner_id != current_user_id and not await uow.company_members.find_one(
                    company_id=quiz.company_id, user_id=current_user_id, is_admin=True):
                raise PermissionDenied("You do not have permission to delete this question")
            total_questions = await uow.questions.count_all(quiz_id=quiz.id)
            if total_questions <= QuestionService.MIN_QUESTIONS:
                raise PermissionDenied(f"A quiz must have at least {QuestionService.MIN_QUESTIONS} questions.")
            await uow.questions.delete_one(question_id)

    @staticmethod
    async def get_questions_by_quiz_id(uow: IUnitOfWork, quiz_id: int, current_user_id: int, skip: int, limit: int) -> \
            List[QuestionSchemaResponse]:
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            if not quiz:
                raise QuizNotFound("Quiz not found")
            company = await uow.companies.find_one(id=quiz.company_id)
            if company.owner_id != current_user_id and not await uow.company_members.find_one(
                    company_id=quiz.company_id, user_id=current_user_id):
                raise PermissionDenied("You do not have permission to view questions in this quiz")

            questions = await uow.questions.find_all(quiz_id=quiz_id, skip=skip, limit=limit)
            return [QuestionSchemaResponse.model_validate(question) for question in questions]
