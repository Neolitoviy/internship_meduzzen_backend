from typing import List

from fastapi import APIRouter, Depends, Request, status

from app.routers.dependencies import CurrentUserDep, QuizServiceDep, UOWDep
from app.schemas.quiz import (
    CreateQuizRequest,
    QuizSchemaResponse,
    QuizzesListResponse,
    UpdateQuizRequest,
)
from app.services.quiz import QuizService

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
)


@router.post("/", response_model=QuizSchemaResponse)
async def create_quiz(
    request: CreateQuizRequest,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuizServiceDep,
):
    return await service.create_quiz(uow, request, current_user.id)


@router.get("/", response_model=QuizzesListResponse)
async def get_quizzes(
    request: Request,
    company_id: int,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuizServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_quizzes(
        uow, company_id, skip, limit, current_user.id, str(request.url)
    )


@router.put("/{quiz_id}", response_model=QuizSchemaResponse)
async def update_quiz(
    quiz_id: int,
    request: UpdateQuizRequest,
    uow: UOWDep,
    current_user: CurrentUserDep,
    service: QuizServiceDep,
):
    return await service.update_quiz(uow, quiz_id, request, current_user.id)


@router.delete("/{quiz_id}", status_code=204)
async def delete_quiz(
    quiz_id: int, uow: UOWDep, current_user: CurrentUserDep, service: QuizServiceDep
):
    await service.delete_quiz(uow, quiz_id, current_user.id)
