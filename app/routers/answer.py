from fastapi import APIRouter, status

from app.routers.dependencies import AnswerServiceDep, CurrentUserDep, UOWDep
from app.schemas.answer import (
    AnswerSchemaCreate,
    AnswerSchemaResponse,
    AnswerSchemaUpdate,
)

router = APIRouter(
    prefix="/answersss",
    tags=["AnswersSS"],
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
    return await service.update_answer(uow, answer_id, answer_data, current_user.id)


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int, uow: UOWDep, current_user: CurrentUserDep, service: AnswerServiceDep
):
    await service.delete_answer(uow, answer_id, current_user.id)
