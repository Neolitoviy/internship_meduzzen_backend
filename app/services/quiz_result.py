from app.db.redis_client import save_quiz_vote_to_redis
from app.schemas.quiz_result import QuizResultResponse, QuizVoteRequest, QuizVoteCreate
from app.utils.unitofwork import IUnitOfWork
from app.core.exceptions import QuizNotFound, PermissionDenied, QuestionNotFound, AnswerNotFound
from datetime import datetime


class QuizResultService:
    @staticmethod
    async def quiz_vote(uow: IUnitOfWork, company_id: int, quiz_id: int, vote_data: QuizVoteRequest,
                        user_id: int) -> QuizResultResponse:
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            if not quiz:
                raise QuizNotFound("Quiz not found")

            company = await uow.companies.find_one(id=quiz.company_id)
            if company.owner_id != user_id and not await uow.company_members.find_one(company_id=company_id,
                                                                                      user_id=user_id, is_admin=True):
                raise PermissionDenied("You do not have permission to take this quiz.")

            total_questions = 0
            total_answers = 0
            for question_id, answer_id in vote_data.answers.items():
                question = await uow.questions.find_one(id=question_id)
                if not question or question.quiz_id != quiz_id:
                    raise QuestionNotFound(f"Question {question_id} not found in quiz {quiz_id}")

                answer = await uow.answers.find_one(id=answer_id)
                if not answer or answer.question_id != question_id:
                    raise AnswerNotFound(f"Answer {answer_id} not found for question {question_id}")

                is_correct = answer.is_correct
                if is_correct:
                    total_answers += 1
                total_questions += 1

                vote = QuizVoteCreate(
                    user_id=user_id,
                    company_id=company_id,
                    quiz_id=quiz_id,
                    question_id=question_id,
                    answer=answer.answer_text,
                    is_correct=is_correct
                )
                await save_quiz_vote_to_redis(vote)

            score = round((total_answers / total_questions) * 100, 2)

            quiz_result = await uow.quiz_results.add_one({
                'user_id': user_id,
                'quiz_id': quiz_id,
                'company_id': company_id,
                'total_questions': total_questions,
                'total_answers': total_answers,
                'score': score,
                'created_at': datetime.utcnow()
            })
            await uow.commit()
            return QuizResultResponse.model_validate(quiz_result)

    @staticmethod
    async def get_user_average_score(uow: IUnitOfWork, user_id: int) -> float:
        async with uow:
            return await uow.quiz_results.get_average_score(user_id=user_id)

    @staticmethod
    async def get_company_average_score(uow: IUnitOfWork, company_id: int, user_id: int) -> float:
        async with uow:
            company = await uow.companies.find_one(id=company_id)
            if company.owner_id != user_id and not await uow.company_members.find_one(company_id=company_id,
                                                                                      user_id=user_id, is_admin=True):
                raise PermissionDenied("You do not have permission to view this company's average score.")
            return await uow.quiz_results.get_average_score(company_id=company_id)