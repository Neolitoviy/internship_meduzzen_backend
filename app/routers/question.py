from typing import List

from fastapi import APIRouter, status

from app.routers.dependencies import (
    AnswerServiceDep,
    CurrentUserDep,
    QuestionServiceDep,
    UOWDep,
)
from app.schemas.answer import AnswerSchemaResponse
from app.schemas.question import (
    QuestionSchemaCreate,
    QuestionSchemaResponse,
    UpdateQuestionRequest,
)

router = APIRouter(
    prefix="/question",
    tags=["Question"],
)


@router.post(
    "/{quiz_id}/",
    response_model=QuestionSchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    quiz_id: int,
    question_data: QuestionSchemaCreate,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuestionServiceDep,
):
    return await service.create_question(uow, quiz_id, question_data, current_user.id)


@router.put(
    "/{question_id}",
    response_model=QuestionSchemaResponse,
    status_code=status.HTTP_200_OK,
)
async def update_question(
    question_id: int,
    question_data: UpdateQuestionRequest,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuestionServiceDep,
):
    return await service.update_question(
        uow, question_id, question_data, current_user.id
    )


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuestionServiceDep,
):
    await service.delete_question(uow, question_id, current_user.id)


@router.get(
    "/{question_id}/answers",
    response_model=List[AnswerSchemaResponse],
    status_code=status.HTTP_200_OK,
)
async def get_answers_by_question_id(
    question_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: AnswerServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_answers_by_question_id(
        uow, question_id, current_user.id, skip, limit
    )
