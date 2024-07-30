from typing import List

from fastapi import APIRouter, Response, status

from app.routers.dependencies import CurrentUserDep, QuizResultServiceDep, UOWDep
from app.schemas.quiz_result import QuizResultResponse, QuizVoteRequest, UserQuizVote

router = APIRouter(
    prefix="/quiz-results",
    tags=["QuizResults"],
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


@router.get("/users/{user_id}/score", response_model=float)
async def get_user_average_score(
    user_id: int,
    company_id: int,
    current_user: CurrentUserDep,
    uow: UOWDep,
    quiz_result_service: QuizResultServiceDep,
):
    return await quiz_result_service.get_user_average_score(
        uow, user_id, company_id, current_user.id
    )


@router.get("/companies/{company_id}/score", response_model=float)
async def get_company_average_score(
    company_id: int,
    uow: UOWDep,
    quiz_result_service: QuizResultServiceDep,
    current_user: CurrentUserDep,
):
    return await quiz_result_service.get_company_average_score(
        uow, company_id, current_user.id
    )


@router.get("/vote-redis")
async def get_vote_redis(
    user_id: int,
    company_id: int,
    quiz_id: int,
    question_id: int,
    current_user: CurrentUserDep,
    uow: UOWDep,
    quiz_result_service: QuizResultServiceDep,
):
    return await quiz_result_service.get_vote_redis(
        uow, current_user.id, user_id, company_id, quiz_id, question_id
    )


@router.get("/quiz-votes-redis", response_model=List[UserQuizVote])
async def get_quiz_votes_redis(
    user_id: int,
    company_id: int,
    quiz_id: int,
    current_user: CurrentUserDep,
    uow: UOWDep,
    quiz_result_service: QuizResultServiceDep,
):
    return await quiz_result_service.get_quiz_votes_from_redis(
        uow, current_user.id, user_id, company_id, quiz_id
    )


@router.get(
    "/export-quiz-results/{company_id}/{quiz_id}/csv", status_code=status.HTTP_200_OK
)
async def export_quiz_results_to_csv(
    user_id: int,
    company_id: int,
    quiz_id: int,
    current_user: CurrentUserDep,
    uow: UOWDep,
    quiz_result_service: QuizResultServiceDep,
):
    csv_data = await quiz_result_service.export_quiz_results_from_redis_to_csv(
        uow, current_user.id, user_id, company_id, quiz_id
    )
    response = Response(content=csv_data, media_type="text/csv")
    response.headers["Content-Disposition"] = (
        f"attachment; filename=quiz_results_{company_id}_{quiz_id}.csv"
    )
    return response


@router.get(
    "/export-quiz-results/{company_id}/{quiz_id}/json",
    response_model=List[UserQuizVote],
    status_code=status.HTTP_200_OK,
)
async def export_quiz_results_to_json(
    user_id: int,
    company_id: int,
    quiz_id: int,
    current_user: CurrentUserDep,
    uow: UOWDep,
    quiz_result_service: QuizResultServiceDep,
):
    json_data = await quiz_result_service.export_quiz_results_from_redis_to_json(
        uow, current_user.id, user_id, company_id, quiz_id
    )
    response = Response(content=json_data, media_type="application/json")
    response.headers["Content-Disposition"] = (
        f"attachment; filename=quiz_results_{company_id}_{quiz_id}.json"
    )
    return response
