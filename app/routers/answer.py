from typing import List

from fastapi import APIRouter, Depends, status

from app.routers.dependencies import AnswerServiceDep, CurrentUserDep, UOWDep
from app.schemas.answer import (
    AnswerSchemaCreate,
    AnswerSchemaResponse,
    AnswerSchemaUpdate,
)
from app.services.answer import AnswerService

router = APIRouter(
    prefix="/answer",
    tags=["Answer"],
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


@router.put("/{answer_id}", response_model=AnswerSchemaResponse)
async def update_answer(
    answer_id: int,
    answer_data: AnswerSchemaUpdate,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: AnswerServiceDep,
):
    return await service.update_answer(uow, answer_id, answer_data, current_user.id)


@router.delete("/{answer_id}", status_code=204)
async def delete_answer(
    answer_id: int, uow: UOWDep, current_user: CurrentUserDep, service: AnswerServiceDep
):
    await service.delete_answer(uow, answer_id, current_user.id)


@router.get(
    "/question/{question_id}/answers", response_model=List[AnswerSchemaResponse]
)
async def get_answers_by_question_id(
    question_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: AnswerService = Depends(),
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_answers_by_question_id(
        uow, question_id, current_user.id, skip, limit
    )
