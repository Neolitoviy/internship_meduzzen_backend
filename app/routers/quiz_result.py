from datetime import datetime
from typing import List

from fastapi import APIRouter, Response, status

from app.routers.dependencies import CurrentUserDep, QuizResultServiceDep, UOWDep
from app.schemas.analytics import (
    CompanyMemberAverageScore,
    CompanyUserLastAttempt,
    LastQuizAttempt,
    QuizScore,
    QuizTrend,
)
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


@router.get(
    "/companies/{company_id}/users/{user_id}/score",
    response_model=float,
)
async def get_user_company_average_score(
    user_id: int,
    company_id: int,
    uow: UOWDep,
    quiz_result_service: QuizResultServiceDep,
    current_user: CurrentUserDep,
):
    return await quiz_result_service.get_company_average_score(
        uow, user_id, company_id, current_user.id
    )


@router.get("/user/quiz-scores", response_model=List[QuizScore])
async def get_user_quiz_scores(
    current_user: CurrentUserDep,
    uow: UOWDep,
    service: QuizResultServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_user_quiz_scores(uow, current_user.id, skip, limit)


@router.get("/user/last-quiz-attempts", response_model=List[LastQuizAttempt])
async def get_user_last_quiz_attempts(
    current_user: CurrentUserDep,
    uow: UOWDep,
    service: QuizResultServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_user_last_quiz_attempts(uow, current_user.id, skip, limit)


@router.get(
    "/companies/{company_id}/members-average-scores",
    response_model=List[CompanyMemberAverageScore],
)
async def get_company_members_average_scores(
    company_id: int,
    start_date: datetime,
    end_date: datetime,
    current_user: CurrentUserDep,
    uow: UOWDep,
    service: QuizResultServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_company_members_average_scores_over_time(
        uow, company_id, start_date, end_date, current_user.id, skip, limit
    )


@router.get(
    "/companies/{company_id}/user/{user_id}/quiz-trends", response_model=List[QuizTrend]
)
async def get_user_quiz_trends(
    company_id: int,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    current_user: CurrentUserDep,
    uow: UOWDep,
    service: QuizResultServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_user_quiz_trends(
        uow, company_id, user_id, start_date, end_date, current_user.id, skip, limit
    )


@router.get(
    "/companies/{company_id}/user-last-attempts",
    response_model=List[CompanyUserLastAttempt],
)
async def get_company_user_last_attempts(
    company_id: int,
    current_user: CurrentUserDep,
    uow: UOWDep,
    service: QuizResultServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.get_company_user_last_attempts(
        uow, company_id, current_user.id, skip, limit
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
