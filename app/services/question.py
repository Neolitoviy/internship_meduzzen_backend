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
    """
    Service for handling operations related to questions.

    Attributes:
        MIN_QUESTIONS (int): Minimum number of questions required for a quiz.
    """
    MIN_QUESTIONS = 2

    @staticmethod
    async def create_question(
        uow: IUnitOfWork,
        quiz_id: int,
        question_data: QuestionSchemaCreate,
        current_user_id: int,
    ) -> QuestionSchemaResponse:
        """
        Create a new question for a quiz.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            quiz_id (int): ID of the quiz to which the question belongs.
            question_data (QuestionSchemaCreate): Data for the new question.
            current_user_id (int): ID of the user creating the question.

        Returns:
            QuestionSchemaResponse: The created question.

        Raises:
            PermissionDenied: If the user does not have permission to create the question.
        """
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
        """
        Update an existing question.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            question_id (int): ID of the question to be updated.
            question_data (UpdateQuestionRequest): Updated data for the question.
            current_user_id (int): ID of the user updating the question.

        Returns:
            QuestionSchemaResponse: The updated question.

        Raises:
            PermissionDenied: If the user does not have permission to update the question.
        """
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
        """
        Delete a question.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            question_id (int): ID of the question to be deleted.
            current_user_id (int): ID of the user deleting the question.

        Raises:
            PermissionDenied: If the user does not have permission to delete the question
            or if the quiz has fewer than the minimum number of questions.
        """
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
        """
        Get questions for a quiz.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            quiz_id (int): ID of the quiz.
            current_user_id (int): ID of the user requesting the questions.
            skip (int): Number of items to skip for pagination.
            limit (int): Maximum number of items to return.

        Returns:
            List[QuestionSchemaResponse]: List of questions for the quiz.

        Raises:
            PermissionDenied: If the user does not have permission to view the questions.
        """
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
        """
        Check if a quiz has at least the minimum number of questions.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            quiz_id (int): ID of the quiz.

        Raises:
            PermissionDenied: If the quiz has fewer than the minimum number of questions.
        """
        total_questions = await uow.questions.count_all(quiz_id=quiz_id)
        if total_questions <= QuestionService.MIN_QUESTIONS:
            raise PermissionDenied(
                f"A quiz must have at least {QuestionService.MIN_QUESTIONS} questions."
            )
