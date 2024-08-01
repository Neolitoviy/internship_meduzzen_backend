from typing import List

from fastapi import APIRouter, Request, status

from app.routers.dependencies import (
    CurrentUserDep,
    QuestionServiceDep,
    QuizServiceDep,
    UOWDep,
)
from app.schemas.question import QuestionSchemaResponse
from app.schemas.quiz import (
    CreateQuizRequest,
    QuizSchemaResponse,
    QuizzesListResponse,
    UpdateQuizRequest,
)

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"],
)


@router.post(
    "/", response_model=QuizSchemaResponse, status_code=status.HTTP_201_CREATED
)
async def create_quiz(
    request: CreateQuizRequest,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuizServiceDep,
):
    """
    Create a new quiz.

    Args:
        request (CreateQuizRequest): The request data for creating a quiz.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (QuizServiceDep): The quiz service dependency.

    Returns:
        QuizSchemaResponse: The newly created quiz.
    """
    return await service.create_quiz(uow, request, current_user.id)


@router.get("/", response_model=QuizzesListResponse, status_code=status.HTTP_200_OK)
async def get_quizzes(
    request: Request,
    company_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuizServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    """
    Get a paginated list of quizzes.

    Args:
        request (Request): The HTTP request object.
        company_id (int): The ID of the company.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (QuizServiceDep): The quiz service dependency.
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return for pagination.

    Returns:
        QuizzesListResponse: A paginated list of quizzes.
    """
    return await service.get_quizzes(
        uow, company_id, skip, limit, current_user.id, str(request.url)
    )


@router.put(
    "/{quiz_id}", response_model=QuizSchemaResponse, status_code=status.HTTP_200_OK
)
async def update_quiz(
    quiz_id: int,
    request: UpdateQuizRequest,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuizServiceDep,
):
    """
    Update an existing quiz.

    Args:
        quiz_id (int): The ID of the quiz to update.
        request (UpdateQuizRequest): The request data for updating the quiz.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (QuizServiceDep): The quiz service dependency.

    Returns:
        QuizSchemaResponse: The updated quiz.
    """
    return await service.update_quiz(uow, quiz_id, request, current_user.id)


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int, uow: UOWDep, current_user: CurrentUserDep, service: QuizServiceDep
):
    """
    Delete an existing quiz.

    Args:
        quiz_id (int): The ID of the quiz to delete.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (QuizServiceDep): The quiz service dependency.

    Returns:
        None
    """
    await service.delete_quiz(uow, quiz_id, current_user.id)


@router.get(
    "/{quiz_id}",
    response_model=List[QuestionSchemaResponse],
    status_code=status.HTTP_200_OK,
)
async def get_questions_by_quiz_id(
    quiz_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuestionServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    """
    Get a paginated list of questions for a specific quiz.

    Args:
        quiz_id (int): The ID of the quiz.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (QuestionServiceDep): The question service dependency.
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return for pagination.

    Returns:
        List[QuestionSchemaResponse]: A paginated list of questions for the quiz.
    """
    return await service.get_questions_by_quiz_id(
        uow, quiz_id, current_user.id, skip, limit
    )
