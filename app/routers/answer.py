from fastapi import APIRouter, status

from app.routers.dependencies import AnswerServiceDep, CurrentUserDep, UOWDep
from app.schemas.answer import (
    AnswerSchemaCreate,
    AnswerSchemaResponse,
    AnswerSchemaUpdate,
)

router = APIRouter(
    prefix="/answers",
    tags=["Answers"],
)


@router.post(
    "/{question_id}/",
    response_model=AnswerSchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_answer(
    question_id: int,
    answer_data: AnswerSchemaCreate,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: AnswerServiceDep,
):
    """
    Create a new answer for a specific question.

    Args:
        question_id (int): The ID of the question.
        answer_data (AnswerSchemaCreate): The data for the new answer.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (AnswerServiceDep): The answer service dependency.

    Returns:
        AnswerSchemaResponse: The newly created answer.
    """
    return await service.create_answer(uow, question_id, answer_data, current_user.id)


@router.put(
    "/{answer_id}", response_model=AnswerSchemaResponse, status_code=status.HTTP_200_OK
)
async def update_answer(
    answer_id: int,
    answer_data: AnswerSchemaUpdate,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: AnswerServiceDep,
):
    """
    Update an existing answer.

    Args:
        answer_id (int): The ID of the answer to update.
        answer_data (AnswerSchemaUpdate): The data for updating the answer.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (AnswerServiceDep): The answer service dependency.

    Returns:
        AnswerSchemaResponse: The updated answer.
    """
    return await service.update_answer(uow, answer_id, answer_data, current_user.id)


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int, uow: UOWDep, current_user: CurrentUserDep, service: AnswerServiceDep
):
    """
    Delete an existing answer.

    Args:
        answer_id (int): The ID of the answer to delete.
        uow (UOWDep): The unit of work dependency.
        current_user (CurrentUserDep): The current authenticated user.
        service (AnswerServiceDep): The answer service dependency.

    Returns:
        None
    """
    await service.delete_answer(uow, answer_id, current_user.id)
