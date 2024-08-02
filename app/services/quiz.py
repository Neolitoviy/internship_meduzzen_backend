from app.schemas.notification import NotificationCreate
from app.schemas.quiz import (
    CreateQuizRequest,
    QuizSchemaResponse,
    QuizzesListResponse,
    UpdateQuizRequest,
)
from app.services.company import CompanyService
from app.utils.pagination import paginate
from app.utils.unitofwork import IUnitOfWork


class QuizService:
    """
    Service class for managing quizzes.

    Provides methods to create, retrieve, update, and delete quizzes, as well as send notifications to company members.
    """

    @staticmethod
    async def create_quiz(
        uow: IUnitOfWork, quiz_data: CreateQuizRequest, current_user_id: int
    ) -> QuizSchemaResponse:
        """
        Create a new quiz and send notifications to company members.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            quiz_data (CreateQuizRequest): Data for creating the quiz.
            current_user_id (int): ID of the user creating the quiz.

        Returns:
            QuizSchemaResponse: The created quiz.

        Raises:
            CompanyPermissionError: If the user does not have permission to create a quiz for the company.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, quiz_data.company_id, current_user_id, is_admin=True
            )

            new_quiz = await uow.quizzes.add_one(
                {
                    "title": quiz_data.title,
                    "description": quiz_data.description,
                    "frequency_in_days": quiz_data.frequency_in_days,
                    "company_id": quiz_data.company_id,
                    "user_id": current_user_id,
                }
            )

            # Send notifications to company members
            company_members = await uow.company_members.find_all(
                company_id=quiz_data.company_id
            )
            for member in company_members:
                notification = NotificationCreate(
                    user_id=member.user_id,
                    quiz_id=new_quiz.id,
                    message=f"A new quiz '{new_quiz.title}' has been created. You are invited to participate.",
                )
                await uow.notifications.add_one(notification.model_dump())

            for question_data in quiz_data.questions_data:
                new_question = await uow.questions.add_one(
                    {
                        "question_text": question_data.question_text,
                        "quiz_id": new_quiz.id,
                    }
                )

                for answer_data in question_data.answers:
                    await uow.answers.add_one(
                        {
                            "answer_text": answer_data.answer_text,
                            "is_correct": answer_data.is_correct,
                            "question_id": new_question.id,
                        }
                    )

            return QuizSchemaResponse.model_validate(new_quiz)

    @staticmethod
    async def get_quizzes(
        uow: IUnitOfWork,
        company_id: int,
        skip: int,
        limit: int,
        current_user_id: int,
        request_url: str,
    ) -> QuizzesListResponse:
        """
        Retrieve a list of quizzes for a company with pagination.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            company_id (int): ID of the company.
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.
            current_user_id (int): ID of the user making the request.
            request_url (str): URL of the request for generating pagination links.

        Returns:
            QuizzesListResponse: Paginated list of quizzes.

        Raises:
            CompanyPermissionError: If the user does not have permission to view the company's quizzes.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id
            )

            total_quizzes = await uow.quizzes.count_all(company_id=company_id)
            quizzes = await uow.quizzes.find_all(
                skip=skip, limit=limit, company_id=company_id
            )

            quizzes_response = [
                QuizSchemaResponse.model_validate(quiz) for quiz in quizzes
            ]
            pagination_response = paginate(
                items=quizzes_response,
                total_items=total_quizzes,
                skip=skip,
                limit=limit,
                request_url=request_url,
            )

            return QuizzesListResponse(
                total_pages=pagination_response.total_pages,
                current_page=pagination_response.current_page,
                items=pagination_response.items,
                pagination=pagination_response.pagination,
            )

    @staticmethod
    async def update_quiz(
        uow: IUnitOfWork,
        quiz_id: int,
        update_data: UpdateQuizRequest,
        current_user_id: int,
    ) -> QuizSchemaResponse:
        """
        Update an existing quiz.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            quiz_id (int): ID of the quiz to be updated.
            update_data (UpdateQuizRequest): Data for updating the quiz.
            current_user_id (int): ID of the user updating the quiz.

        Returns:
            QuizSchemaResponse: The updated quiz.

        Raises:
            CompanyPermissionError: If the user does not have permission to update the quiz.
            RecordNotFound: If the quiz does not exist.
        """
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )
            updated_quiz = await uow.quizzes.edit_one(quiz_id, update_data.model_dump())
            return QuizSchemaResponse.model_validate(updated_quiz)

    @staticmethod
    async def delete_quiz(uow: IUnitOfWork, quiz_id: int, current_user_id: int) -> None:
        """
        Delete a quiz.

        Args:
            uow (IUnitOfWork): Unit of work for database operations.
            quiz_id (int): ID of the quiz to be deleted.
            current_user_id (int): ID of the user deleting the quiz.

        Returns:
            None

        Raises:
            CompanyPermissionError: If the user does not have permission to delete the quiz.
            RecordNotFound: If the quiz does not exist.
        """
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )
            await uow.quizzes.delete_one(quiz_id)
