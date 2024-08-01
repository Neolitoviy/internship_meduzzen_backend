from typing import List

from app.core.exceptions import PermissionDenied
from app.schemas.answer import (
    AnswerSchemaCreate,
    AnswerSchemaResponse,
    AnswerSchemaUpdate,
)
from app.services.company import CompanyService
from app.utils.unitofwork import IUnitOfWork


class AnswerService:
    """
    Service class for managing answers.

    This class provides methods for creating, updating, deleting, and retrieving answers
    associated with questions and quizzes. It ensures that the user has the necessary
    permissions and that the minimum number of answers is maintained.
    """
    MIN_ANSWERS = 2

    @staticmethod
    async def create_answer(
        uow: IUnitOfWork,
        question_id: int,
        answer_data: AnswerSchemaCreate,
        current_user_id: int,
    ) -> AnswerSchemaResponse:
        """
        Create a new answer for a given question.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            question_id (int): The ID of the question to add the answer to.
            answer_data (AnswerSchemaCreate): The data for the new answer.
            current_user_id (int): The ID of the current user.

        Returns:
            AnswerSchemaResponse: The created answer.

        Raises:
            CompanyPermissionError: If the user does not have permission to create an answer.
        """
        async with uow:
            question = await uow.questions.find_one(id=question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
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
        """
        Update an existing answer.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            answer_id (int): The ID of the answer to update.
            answer_data (AnswerSchemaUpdate): The new data for the answer.
            current_user_id (int): The ID of the current user.

        Returns:
            AnswerSchemaResponse: The updated answer.

        Raises:
            CompanyPermissionError: If the user does not have permission to update the answer.
        """
        async with uow:
            answer = await uow.answers.find_one(id=answer_id)
            question = await uow.questions.find_one(id=answer.question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )
            updated_answer = await uow.answers.edit_one(
                answer_id, answer_data.model_dump(exclude_unset=True)
            )
            return AnswerSchemaResponse.model_validate(updated_answer)

    @staticmethod
    async def delete_answer(
        uow: IUnitOfWork, answer_id: int, current_user_id: int
    ) -> None:
        """
        Delete an existing answer.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            answer_id (int): The ID of the answer to delete.
            current_user_id (int): The ID of the current user.

        Raises:
            CompanyPermissionError: If the user does not have permission to delete the answer.
            PermissionDenied: If the question does not have at least the minimum number of answers.
        """
        async with uow:
            answer = await uow.answers.find_one(id=answer_id)
            question = await uow.questions.find_one(id=answer.question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )
            await AnswerService.check_min_answers(uow, question.id)
            await uow.answers.delete_one(answer_id)

    @staticmethod
    async def get_answers_by_question_id(
            uow: IUnitOfWork, question_id: int, current_user_id: int, skip: int, limit: int
    ) -> List[AnswerSchemaResponse]:
        """
        Retrieve answers for a given question.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            question_id (int): The ID of the question.
            current_user_id (int): The ID of the current user.
            skip (int): The number of items to skip (for pagination).
            limit (int): The maximum number of items to return (for pagination).

        Returns:
            List[AnswerSchemaResponse]: A list of answers for the question.

        Raises:
            CompanyPermissionError: If the user does not have permission to view the answers.
        """
        async with uow:
            question = await uow.questions.find_one(id=question_id)
            quiz = await uow.quizzes.find_one(id=question.quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id
            )
            answers = await uow.answers.find_all(
                skip=skip, limit=limit, question_id=question_id
            )
            return [AnswerSchemaResponse.model_validate(answer) for answer in answers]

    @staticmethod
    async def check_min_answers(uow: IUnitOfWork, question_id: int) -> None:
        """
        Ensure that a question has at least the minimum number of answers.

        Args:
            uow (IUnitOfWork): The unit of work for database operations.
            question_id (int): The ID of the question.

        Raises:
            PermissionDenied: If the question does not have at least the minimum number of answers.
        """
        total_answers = await uow.answers.count_all(question_id=question_id)
        if total_answers <= AnswerService.MIN_ANSWERS:
            raise PermissionDenied(
                f"A question must have at least {AnswerService.MIN_ANSWERS} answers."
            )
