from fastapi import APIRouter, Depends
from typing import List

from app.schemas.question import QuestionSchemaCreate, QuestionSchemaResponse, UpdateQuestionRequest
from app.services.question import QuestionService
from app.routers.dependencies import UOWDep, CurrentUserDep, QuestionServiceDep

router = APIRouter(
    prefix="/question",
    tags=["Question"],
)


@router.post("/{quiz_id}/", response_model=QuestionSchemaResponse)
async def create_question(
        quiz_id: int,
        question_data: QuestionSchemaCreate,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: QuestionServiceDep
):
    return await service.create_question(uow, quiz_id, question_data, current_user.id)


@router.put("/{question_id}", response_model=QuestionSchemaResponse)
async def update_question(
        question_id: int,
        question_data: UpdateQuestionRequest,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: QuestionServiceDep
):
    return await service.update_question(uow, question_id, question_data, current_user.id)


@router.delete("/{question_id}", status_code=204)
async def delete_question(
        question_id: int,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: QuestionServiceDep
):
    await service.delete_question(uow, question_id, current_user.id)


@router.get("/quiz/{quiz_id}", response_model=List[QuestionSchemaResponse])
async def get_questions_by_quiz_id(
        quiz_id: int,
        uow: UOWDep,
        current_user: CurrentUserDep,
        service: QuestionServiceDep
):
    return await service.get_questions_by_quiz_id(uow, quiz_id, current_user.id)
