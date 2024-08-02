import csv
import json
from datetime import datetime
from io import StringIO
from typing import List

from app.db.redis_db import get_redis_client
from app.schemas.analytics import (
    CompanyMemberAverageScore,
    CompanyUserLastAttempt,
    LastQuizAttempt,
    QuizScore,
    QuizTrend,
)
from app.schemas.quiz_result import QuizResultResponse, QuizVoteRequest, UserQuizVote
from app.services.company import CompanyService
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
        """
        Record a user's vote for a quiz.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            company_id (int): ID of the company.
            quiz_id (int): ID of the quiz.
            vote_data (QuizVoteRequest): Data of the user's votes.
            user_id (int): ID of the user.

        Returns:
            QuizResultResponse: The recorded quiz result.
        """
        async with uow:
            await CompanyService.check_company_permission(uow, company_id, user_id)
            total_questions = 0
            total_answers = 0
            for question_id, answer_id in vote_data.answers.items():
                question = await uow.questions.find_one(id=question_id)
                answer = await uow.answers.find_one(
                    id=answer_id, question_id=question_id
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

            quiz_result = await uow.quiz_results.add_one(
                {
                    "user_id": user_id,
                    "quiz_id": quiz_id,
                    "company_id": company_id,
                    "total_questions": total_questions,
                    "total_answers": total_answers,
                    "score": round((total_answers / total_questions) * 100, 2),
                    "created_at": datetime.utcnow(),
                }
            )
            return QuizResultResponse.model_validate(quiz_result)

    @staticmethod
    async def get_user_average_score(
        uow: IUnitOfWork, user_id: int, company_id: int, current_user_id: int
    ) -> float:
        """
        Get the average quiz score of a user.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            user_id (int): ID of the user.
            company_id (int): ID of the company.
            current_user_id (int): ID of the current user making the request.

        Returns:
            float: The user's average score.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id
            )
            return await uow.quiz_results.get_average_score(user_id=user_id)

    @staticmethod
    async def get_company_average_score(
        uow: IUnitOfWork, user_id: int, company_id: int, current_user_id: int
    ) -> float:
        """
        Get the average quiz score for a company.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            user_id (int): ID of the user.
            company_id (int): ID of the company.
            current_user_id (int): ID of the current user making the request.

        Returns:
            float: The company's average score.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id
            )
            return await uow.quiz_results.get_average_score(
                user_id=user_id, company_id=company_id
            )

    @staticmethod
    async def get_user_quiz_scores(
        uow: IUnitOfWork, user_id: int, skip: int, limit: int
    ) -> List[QuizScore]:
        """
        Get the quiz scores for a user.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            user_id (int): ID of the user.
            skip (int): Number of items to skip for pagination.
            limit (int): Maximum number of items to return.

        Returns:
            List[QuizScore]: List of quiz scores for the user.
        """
        async with uow:
            results = await uow.quiz_results.find_all(
                user_id=user_id, skip=skip, limit=limit
            )
            quiz_scores = {}
            for result in results:
                quiz = await uow.quizzes.find_one(id=result.quiz_id)
                quiz_id = result.quiz_id
                if quiz_id not in quiz_scores:
                    quiz_scores[quiz_id] = {
                        "quiz_id": quiz_id,
                        "quiz_title": quiz.title,
                        "scores": [],
                        "timestamps": [],
                    }
                quiz_scores[quiz_id]["scores"].append(result.score)
                quiz_scores[quiz_id]["timestamps"].append(result.created_at)
            return [QuizScore.model_validate(data) for data in quiz_scores.values()]

    @staticmethod
    async def get_user_last_quiz_attempts(
        uow: IUnitOfWork, user_id: int, skip: int, limit: int
    ) -> List[LastQuizAttempt]:
        """
        Get the last quiz attempts for a user.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            user_id (int): ID of the user.
            skip (int): Number of items to skip for pagination.
            limit (int): Maximum number of items to return.

        Returns:
            List[LastQuizAttempt]: List of last quiz attempts for the user.
        """
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

    @staticmethod
    async def get_company_members_average_scores_over_time(
        uow: IUnitOfWork,
        company_id: int,
        start_date: datetime,
        end_date: datetime,
        current_user_id: int,
        skip: int,
        limit: int,
    ) -> List[CompanyMemberAverageScore]:
        """
        Get the average scores of company members over time.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            company_id (int): ID of the company.
            start_date (datetime): Start date of the period.
            end_date (datetime): End date of the period.
            current_user_id (int): ID of the current user making the request.
            skip (int): Number of items to skip for pagination.
            limit (int): Maximum number of items to return.

        Returns:
            List[CompanyMemberAverageScore]: List of average scores of company members over time.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id, is_admin=True
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

    @staticmethod
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
        """
        Get the quiz trends for a user over a specific date range.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            company_id (int): ID of the company.
            user_id (int): ID of the user.
            start_date (datetime): Start date of the period.
            end_date (datetime): End date of the period.
            current_user_id (int): ID of the current user making the request.
            skip (int): Number of items to skip for pagination.
            limit (int): Maximum number of items to return.

        Returns:
            List[QuizTrend]: List of quiz trends for the user.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id, is_admin=True
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

    @staticmethod
    async def get_company_user_last_attempts(
        uow: IUnitOfWork,
        company_id: int,
        requesting_user_id: int,
        skip: int,
        limit: int,
    ) -> List[CompanyUserLastAttempt]:
        """
        Get the last quiz attempts for all users in a company.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            company_id (int): ID of the company.
            requesting_user_id (int): ID of the user making the request.
            skip (int): Number of items to skip for pagination.
            limit (int): Maximum number of items to return.

        Returns:
            List[CompanyUserLastAttempt]: List of last quiz attempts for all users in the company.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, requesting_user_id, is_admin=True
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
        """
        Save a user's quiz vote to Redis.

        Args:
            vote (UserQuizVote): The user's quiz vote.
        """
        connection = await get_redis_client()
        answer_key = f"quiz_vote:{vote.user_id}:{vote.company_id}:{vote.quiz_id}:{vote.question_id}"

        await connection.setex(answer_key, 172800, json.dumps(vote.model_dump()))

    @staticmethod
    async def get_quiz_votes_from_redis(
        uow: IUnitOfWork,
        current_user_id: int,
        user_id: int,
        company_id: int,
        quiz_id: int,
    ) -> List[UserQuizVote]:
        """
        Get quiz votes from Redis for a specific user and quiz.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            current_user_id (int): ID of the current user making the request.
            user_id (int): ID of the user whose votes are to be retrieved.
            company_id (int): ID of the company.
            quiz_id (int): ID of the quiz.

        Returns:
            List[UserQuizVote]: List of quiz votes.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id, is_admin=True
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
        """
        Get a specific quiz vote from Redis.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            current_user_id (int): ID of the current user making the request.
            user_id (int): ID of the user whose vote is to be retrieved.
            company_id (int): ID of the company.
            quiz_id (int): ID of the quiz.
            question_id (int): ID of the question.

        Returns:
            dict: The quiz vote data.
        """
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id, is_admin=True
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
        """
        Export quiz results from Redis to a CSV format.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            current_user_id (int): ID of the current user making the request.
            user_id (int): ID of the user whose results are to be exported.
            company_id (int): ID of the company.
            quiz_id (int): ID of the quiz.

        Returns:
            str: CSV data of quiz results.
        """
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
            writer.writerow(vote.to_csv_row())

        return output.getvalue()

    @staticmethod
    async def export_quiz_results_from_redis_to_json(
        uow: IUnitOfWork,
        current_user_id: int,
        user_id: int,
        company_id: int,
        quiz_id: int,
    ) -> str:
        """
        Export quiz results from Redis to a JSON format.

        Args:
            uow (IUnitOfWork): Unit of work instance for database operations.
            current_user_id (int): ID of the current user making the request.
            user_id (int): ID of the user whose results are to be exported.
            company_id (int): ID of the company.
            quiz_id (int): ID of the quiz.

        Returns:
            str: JSON data of quiz results.
        """
        quiz_votes = await QuizResultService.get_quiz_votes_from_redis(
            uow, current_user_id, user_id, company_id, quiz_id
        )
        return json.dumps([vote.model_dump() for vote in quiz_votes])
