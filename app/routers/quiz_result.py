import json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Response
from app.routers.dependencies import UOWDep, CurrentUserDep, QuizResultServiceDep
from app.schemas.analytics import QuizScore, LastQuizAttempt, CompanyMemberAverageScore, QuizTrend, \
    CompanyUserLastAttempt
from app.schemas.quiz_result import QuizResultResponse, QuizVoteRequest, UserQuizVote

router = APIRouter(
    prefix="/quiz_result",
    tags=["QuizResult"],
)


@router.post("/quiz_results/vote/{company_id}/{quiz_id}", response_model=QuizResultResponse)
async def quiz_vote(company_id: int, quiz_id: int, vote_data: QuizVoteRequest, uow: UOWDep,
                    current_user: CurrentUserDep, quiz_result_service: QuizResultServiceDep):
    return await quiz_result_service.quiz_vote(uow, company_id, quiz_id, vote_data, current_user.id)


@router.get("/quiz_results/average_score/user/{user_id}", response_model=float)
async def get_user_average_score(
        user_id: int,
        company_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_user_average_score(uow, user_id, company_id, current_user.id)


@router.get("/quiz_results/average_score/user/{user_id}/company/{company_id}", response_model=float)
async def get_user_company_average_score(
        user_id: int,
        company_id: int,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep,
        current_user: CurrentUserDep
):
    return await quiz_result_service.get_company_average_score(uow, user_id, company_id, current_user.id)


@router.get("/user/quiz_scores", response_model=List[QuizScore])
async def get_user_quiz_scores(
        current_user: CurrentUserDep,
        uow: UOWDep,
        service: QuizResultServiceDep,
        skip: int = 0,
        limit: int = 10
):
    return await service.get_user_quiz_scores(uow, current_user.id, skip, limit)


@router.get("/user/last_quiz_attempts", response_model=List[LastQuizAttempt])
async def get_user_last_quiz_attempts(
        current_user: CurrentUserDep,
        uow: UOWDep,
        service: QuizResultServiceDep,
        skip: int = 0,
        limit: int = 10
):
    return await service.get_user_last_quiz_attempts(uow, current_user.id, skip, limit)


@router.get("/company/{company_id}/member_average_scores", response_model=List[CompanyMemberAverageScore])
async def get_company_members_average_scores(
        company_id: int,
        start_date: datetime,
        end_date: datetime,
        current_user: CurrentUserDep,
        uow: UOWDep,
        service: QuizResultServiceDep,
        skip: int = 0,
        limit: int = 10
):
    return await service.get_company_members_average_scores_over_time(uow, company_id, start_date, end_date,
                                                                      current_user.id, skip, limit)


@router.get("/company/{company_id}/user/{user_id}/quiz_trends", response_model=List[QuizTrend])
async def get_user_quiz_trends(
        company_id: int,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        current_user: CurrentUserDep,
        uow: UOWDep,
        service: QuizResultServiceDep
):
    return await service.get_user_quiz_trends(uow, company_id, user_id, start_date, end_date, current_user.id)


@router.get("/company/{company_id}/user_last_attempts", response_model=List[CompanyUserLastAttempt])
async def get_company_user_last_attempts(
        company_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        service: QuizResultServiceDep,
        skip: int = 0,
        limit: int = 10
):
    return await service.get_company_user_last_attempts(uow, company_id, current_user.id, skip, limit)


@router.get("/get_vote_redis")
async def get_vote_redis(
        user_id: int,
        company_id: int,
        quiz_id: int,
        question_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_vote_redis(uow, current_user.id, user_id, company_id, quiz_id, question_id)


@router.get("/get_quiz_votes_redis", response_model=List[UserQuizVote])
async def get_quiz_votes_redis(
        user_id: int,
        company_id: int,
        quiz_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_quiz_votes_from_redis(uow, current_user.id, user_id, company_id, quiz_id)


@router.get("/export_quiz_results/{company_id}/{quiz_id}/csv")
async def export_quiz_results_to_csv(
        user_id: int,
        company_id: int,
        quiz_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    csv_data = await quiz_result_service.export_quiz_results_from_redis_to_csv(uow, current_user.id, user_id,
                                                                               company_id,
                                                                               quiz_id)
    response = Response(content=csv_data, media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=quiz_results_{company_id}_{quiz_id}.csv"
    return response


@router.get("/export_quiz_results/{company_id}/{quiz_id}/json", response_model=List[UserQuizVote])
async def export_quiz_results_to_json(
        user_id: int,
        company_id: int,
        quiz_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    json_data = await quiz_result_service.export_quiz_results_from_redis_to_json(uow, current_user.id, user_id,
                                                                                 company_id,
                                                                                 quiz_id)
    response = Response(content=json_data, media_type="application/json")
    response.headers["Content-Disposition"] = f"attachment; filename=quiz_results_{company_id}_{quiz_id}.json"
    return response
