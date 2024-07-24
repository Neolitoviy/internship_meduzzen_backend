import csv
import json
from datetime import datetime
from io import StringIO
from typing import List

from app.core.exceptions import (
    AnswerNotFound,
    CompanyNotFound,
    PermissionDenied,
    QuestionNotFound,
    QuizNotFound,
)
from app.db.redis_db import get_redis_client
from app.schemas.analytics import (
    CompanyMemberAverageScore,
    CompanyUserLastAttempt,
    LastQuizAttempt,
    QuizScore,
    QuizTrend,
)
from app.schemas.quiz_result import QuizResultResponse, QuizVoteRequest, UserQuizVote
from app.utils.unitofwork import IUnitOfWork


class QuizResultService:
    @staticmethod
    async def quiz_vote(
        uow: IUnitOfWork,
        company_id: int,
        quiz_id: int,
        vote_data: QuizVoteRequest,
        user_id: int,
    ) -> QuizResultResponse:
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            if not quiz:
                raise QuizNotFound("Quiz not found")

            company = await uow.companies.find_one(id=quiz.company_id)
            if company.owner_id != user_id and not await uow.company_members.find_one(
                company_id=company_id, user_id=user_id
            ):
                raise PermissionDenied("You do not have permission to take this quiz.")

            total_questions = 0
            total_answers = 0
            for question_id, answer_id in vote_data.answers.items():
                question = await uow.questions.find_one(id=question_id)
                if not question or question.quiz_id != quiz_id:
                    raise QuestionNotFound(
                        f"Question {question_id} not found in quiz {quiz_id}"
                    )

                answer = await uow.answers.find_one(id=answer_id)
                if not answer or answer.question_id != question_id:
                    raise AnswerNotFound(
                        f"Answer {answer_id} not found for question {question_id}"
                    )

                is_correct = answer.is_correct
                if is_correct:
                    total_answers += 1
                total_questions += 1

                vote = UserQuizVote(
                    user_id=user_id,
                    company_id=company_id,
                    quiz_id=quiz_id,
                    question_id=question_id,
                    question_text=question.question_text,
                    answer_text=answer.answer_text,
                    is_correct=is_correct,
                )
                await QuizResultService.save_quiz_vote_to_redis(vote)

            score = round((total_answers / total_questions) * 100, 2)

            quiz_result = await uow.quiz_results.add_one(
                {
                    "user_id": user_id,
                    "quiz_id": quiz_id,
                    "company_id": company_id,
                    "total_questions": total_questions,
                    "total_answers": total_answers,
                    "score": score,
                    "created_at": datetime.utcnow(),
                }
            )
            return QuizResultResponse.model_validate(quiz_result)

    @staticmethod  # Already done BE 15 1 1 in previous tasks
    async def get_user_average_score(
        uow: IUnitOfWork, user_id: int, company_id: int, current_user_id: int
    ) -> float:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if (
                company.owner_id != current_user_id
                and not await uow.company_members.find_one(
                    company_id=company_id, user_id=current_user_id
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to view this user's average score."
                )
            return await uow.quiz_results.get_average_score(user_id=user_id)

    @staticmethod
    async def get_company_average_score(
        uow: IUnitOfWork, user_id: int, company_id: int, current_user_id: int
    ) -> float:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if (
                company.owner_id != current_user_id
                and not await uow.company_members.find_one(
                    company_id=company_id, user_id=current_user_id
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to view this company's average score."
                )
            return await uow.quiz_results.get_average_score(
                user_id=user_id, company_id=company_id
            )

    @staticmethod  # BE 15 1 2
    async def get_user_quiz_scores(
        uow: IUnitOfWork, user_id: int, skip: int, limit: int
    ) -> List[QuizScore]:
        async with uow:
            results = await uow.quiz_results.find_all(
                user_id=user_id, skip=skip, limit=limit
            )
            quiz_scores = {}
            for result in results:
                quiz = await uow.quizzes.find_one(id=result.quiz_id)
                quiz_id = result.quiz_id
                if quiz_id not in quiz_scores:  # Each means unique quiz_id
                    quiz_scores[quiz_id] = {
                        "quiz_id": quiz_id,
                        "quiz_title": quiz.title,
                        "scores": [],
                        "timestamps": [],
                    }
                quiz_scores[quiz_id]["scores"].append(
                    result.score
                )  # List of average score for Each quiz
                quiz_scores[quiz_id]["timestamps"].append(
                    result.created_at
                )  # Time ranges
            return [QuizScore.model_validate(data) for data in quiz_scores.values()]

    @staticmethod  # BE 15 1 3
    async def get_user_last_quiz_attempts(
        uow: IUnitOfWork, user_id: int, skip: int, limit: int
    ) -> List[LastQuizAttempt]:
        async with uow:
            results = await uow.quiz_results.find_all(
                user_id=user_id, skip=skip, limit=limit
            )
            last_attempts = {}
            for result in results:
                quiz_id = result.quiz_id
                if (
                    quiz_id not in last_attempts
                    or result.created_at > last_attempts[quiz_id]["timestamp"]
                ):
                    last_attempts[quiz_id] = {
                        "quiz_id": quiz_id,
                        "timestamp": result.created_at,
                    }
            return [
                LastQuizAttempt.model_validate(data) for data in last_attempts.values()
            ]

    @staticmethod  # BE 15 2 1
    async def get_company_members_average_scores_over_time(
        uow: IUnitOfWork,
        company_id: int,
        start_date: datetime,
        end_date: datetime,
        current_user_id: int,
        skip: int,
        limit: int,
    ) -> List[CompanyMemberAverageScore]:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if (
                company.owner_id != current_user_id
                and not await uow.company_members.find_one(
                    company_id=company_id, user_id=current_user_id, is_admin=True
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to view this company's average scores."
                )

            member_scores = await uow.quiz_results.get_company_members_average_scores(
                company_id, start_date, end_date, skip, limit
            )
            return [
                CompanyMemberAverageScore.model_validate(
                    {
                        "user_id": score.user_id,
                        "average_score": round(score.average_score, 2),
                        "start_date": score.start_date,
                        "end_date": score.end_date,
                    }
                )
                for score in member_scores
            ]

    @staticmethod  # BE 15 2 2
    async def get_user_quiz_trends(
        uow: IUnitOfWork,
        company_id: int,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        current_user_id: int,
        skip: int,
        limit: int,
    ) -> List[QuizTrend]:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if (
                company.owner_id != current_user_id
                and not await uow.company_members.find_one(
                    company_id=company_id, user_id=current_user_id, is_admin=True
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to view this user's quiz trends."
                )

            quiz_trends = await uow.quiz_results.get_quiz_trends_by_date_range(
                user_id, start_date, end_date, skip, limit
            )
            quiz_trends_with_averages = []
            for trend in quiz_trends:
                quiz = await uow.quizzes.find_one(id=trend.quiz_id)
                quiz_trends_with_averages.append(
                    {
                        "quiz_id": trend.quiz_id,
                        "quiz_title": quiz.title,
                        "average_score": round(trend.average_score, 2),
                        "start_date": trend.start_date,
                        "end_date": trend.end_date,
                    }
                )

            return [
                QuizTrend.model_validate(data) for data in quiz_trends_with_averages
            ]

    @staticmethod  # BE 15 2 3
    async def get_company_user_last_attempts(
        uow: IUnitOfWork,
        company_id: int,
        requesting_user_id: int,
        skip: int,
        limit: int,
    ) -> List[CompanyUserLastAttempt]:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if (
                company.owner_id != requesting_user_id
                and not await uow.company_members.find_one(
                    company_id=company_id, user_id=requesting_user_id, is_admin=True
                )
            ):
                raise PermissionDenied(
                    "You do not have permission to view this company's user attempts."
                )
            members = await uow.company_members.find_all(
                company_id=company_id, skip=skip, limit=limit
            )
            user_last_attempts = []
            for member in members:
                last_attempt = await uow.quiz_results.find_last_attempt_with_filter(
                    user_id=member.user_id
                )
                user_last_attempts.append(
                    {
                        "user_id": member.user_id,
                        "last_attempt": (
                            last_attempt.created_at if last_attempt else None
                        ),
                    }
                )
            return [
                CompanyUserLastAttempt.model_validate(data)
                for data in user_last_attempts
            ]

    @staticmethod
    async def save_quiz_vote_to_redis(vote: UserQuizVote) -> None:
        connection = await get_redis_client()
        answer_key = f"quiz_vote:{vote.user_id}:{vote.company_id}:{vote.quiz_id}:{vote.question_id}"

        await connection.setex(answer_key, 172800, json.dumps(vote.dict()))

    @staticmethod
    async def get_quiz_votes_from_redis(
        uow: IUnitOfWork,
        current_user_id: int,
        user_id: int,
        company_id: int,
        quiz_id: int,
    ) -> List[UserQuizVote]:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if not company:
                raise QuizNotFound("Company not found")
            if user_id != current_user_id:
                if (
                    company.owner_id != current_user_id
                    and not await uow.company_members.find_one(
                        company_id=company_id, user_id=current_user_id, is_admin=True
                    )
                ):
                    raise PermissionDenied(
                        "You do not have permission to view this company's quiz votes."
                    )
        connection = await get_redis_client()
        user_key_pattern = f"quiz_vote:{user_id}:{company_id}:{quiz_id}:*"
        user_keys = await connection.keys(user_key_pattern)
        quiz_votes = []

        for user_key in user_keys:
            user_key_str = str(user_key)[len("<Future finished result='") : -2].strip()
            answer_data_json = await connection.get(user_key_str)
            if answer_data_json:
                answer_data = json.loads(answer_data_json)
                quiz_votes.append(answer_data)

        return [UserQuizVote.model_validate(vote) for vote in quiz_votes]

    @staticmethod
    async def get_vote_redis(
        uow: IUnitOfWork,
        current_user_id: int,
        user_id: int,
        company_id: int,
        quiz_id: int,
        question_id: int,
    ):
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if not company:
                raise CompanyNotFound("Company not found")
            if user_id != current_user_id:
                if (
                    company.owner_id != current_user_id
                    and not await uow.company_members.find_one(
                        company_id=company_id, user_id=current_user_id, is_admin=True
                    )
                ):
                    raise PermissionDenied(
                        "You do not have permission to view this company's quiz votes."
                    )
        connection = await get_redis_client()
        key = f"quiz_vote:{user_id}:{company_id}:{quiz_id}:{question_id}"
        data = await connection.get(key)
        if data:
            return json.loads(data)
        return {"status": "not found"}

    @staticmethod
    async def export_quiz_results_from_redis_to_csv(
        uow: IUnitOfWork,
        current_user_id: int,
        user_id: int,
        company_id: int,
        quiz_id: int,
    ) -> str:
        quiz_votes = await QuizResultService.get_quiz_votes_from_redis(
            uow, current_user_id, user_id, company_id, quiz_id
        )
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "User ID",
                "Company ID",
                "Quiz ID",
                "Question ID",
                "Question Text",
                "Answer Text",
                "Is Correct",
                "Timestamp",
            ]
        )

        for vote in quiz_votes:
            writer.writerow(
                [
                    vote.user_id,
                    vote.company_id,
                    vote.quiz_id,
                    vote.question_id,
                    vote.question_text,
                    vote.answer_text,
                    vote.is_correct,
                    vote.timestamp,
                ]
            )

        return output.getvalue()

    @staticmethod
    async def export_quiz_results_from_redis_to_json(
        uow: IUnitOfWork,
        current_user_id: int,
        user_id: int,
        company_id: int,
        quiz_id: int,
    ) -> str:
        quiz_votes = await QuizResultService.get_quiz_votes_from_redis(
            uow, current_user_id, user_id, company_id, quiz_id
        )
        return json.dumps([vote.dict() for vote in quiz_votes])
