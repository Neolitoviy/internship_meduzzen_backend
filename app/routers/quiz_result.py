from fastapi import APIRouter, status

from app.routers.dependencies import CurrentUserDep, QuizResultServiceDep, UOWDep
from app.schemas.quiz_result import QuizResultResponse, QuizVoteRequest

router = APIRouter(
    prefix="/quiz_result",
    tags=["QuizResult"],
)


@router.post(
    "/vote/{company_id}/{quiz_id}",
    response_model=QuizResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def quiz_vote(
    company_id: int,
    quiz_id: int,
    vote_data: QuizVoteRequest,
    uow: UOWDep,
    current_user: CurrentUserDep,
    quiz_result_service: QuizResultServiceDep,
):
    return await quiz_result_service.quiz_vote(
        uow, company_id, quiz_id, vote_data, current_user.id
    )


@router.get("/average_score/user/{user_id}", response_model=float)
async def get_user_average_score(
    user_id: int, uow: UOWDep, quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_user_average_score(uow, user_id)


@router.get("/average_score/company/{company_id}", response_model=float)
async def get_company_average_score(
    company_id: int,
    uow: UOWDep,
    quiz_result_service: QuizResultServiceDep,
    current_user: CurrentUserDep,
):
    return await quiz_result_service.get_company_average_score(
        uow, company_id, current_user.id
    )
