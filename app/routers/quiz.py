from typing import List

from fastapi import APIRouter, File, Request, UploadFile, status

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
    return await service.update_quiz(uow, quiz_id, request, current_user.id)


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int, uow: UOWDep, current_user: CurrentUserDep, service: QuizServiceDep
):
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
    return await service.get_questions_by_quiz_id(
        uow, quiz_id, current_user.id, skip, limit
    )


@router.post("/import")
async def import_quizzes(
    company_id: int,
    current_user: CurrentUserDep,
    uow: UOWDep,
    service: QuizServiceDep,
    file: UploadFile = File(...),
):
    await service.validate_file_type(file)
    return await service.import_quizzes(uow, file, current_user.id, company_id)
