from fastapi import APIRouter
from app.routers.dependencies import CurrentUserDep, UOWDep, QuizResultServiceDep
from typing import List, Dict, Any

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/user/overall_rating", response_model=float)
async def get_user_overall_rating(
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_user_overall_rating(uow, current_user.id)


@router.get("/user/quiz_scores", response_model=List[Dict[str, Any]])
async def get_user_quiz_scores(
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_user_quiz_scores(uow, current_user.id)


@router.get("/user/last_quiz_attempts", response_model=List[Dict[str, Any]])
async def get_user_last_quiz_attempts(
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_user_last_quiz_attempts(uow, current_user.id)


@router.get("/company/{company_id}/member_scores", response_model=List[Dict[str, Any]])
async def get_company_member_average_scores(
        company_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_company_member_average_scores(uow, company_id, current_user.id)


@router.get("/company/{company_id}/user/{user_id}/quiz_scores", response_model=List[Dict[str, Any]])
async def get_user_quiz_scores_with_trends(
        company_id: int,
        user_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_user_quiz_scores_with_trends(uow, user_id, company_id, current_user.id)


@router.get("/company/{company_id}/user_last_attempts", response_model=List[Dict[str, Any]])
async def get_company_user_last_attempts(
        company_id: int,
        current_user: CurrentUserDep,
        uow: UOWDep,
        quiz_result_service: QuizResultServiceDep
):
    return await quiz_result_service.get_company_user_last_attempts(uow, company_id, current_user.id)
