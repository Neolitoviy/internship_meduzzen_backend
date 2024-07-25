from app.schemas.quiz import (
    CreateQuizRequest,
    PaginationLinks,
    QuizSchemaResponse,
    QuizzesListResponse,
    UpdateQuizRequest,
)
from app.services.company import CompanyService
from app.utils.unitofwork import IUnitOfWork


class QuizService:
    @staticmethod
    async def create_quiz(
        uow: IUnitOfWork, quiz_data: CreateQuizRequest, current_user_id: int
    ) -> QuizSchemaResponse:
        async with uow:
            await CompanyService.check_company_permission(
                uow, quiz_data.company_id, current_user_id, is_admin=True
            )

            new_quiz = await uow.quizzes.add_one(
                {
                    "title": quiz_data.title,
                    "description": quiz_data.description,
                    "frequency_in_days": quiz_data.frequency_in_days,
                    "company_id": quiz_data.company_id,
                    "user_id": current_user_id,
                }
            )

            for question_data in quiz_data.questions_data:
                new_question = await uow.questions.add_one(
                    {
                        "question_text": question_data.question_text,
                        "quiz_id": new_quiz.id,
                    }
                )

                for answer_data in question_data.answers:
                    await uow.answers.add_one(
                        {
                            "answer_text": answer_data.answer_text,
                            "is_correct": answer_data.is_correct,
                            "question_id": new_question.id,
                        }
                    )

            return QuizSchemaResponse.model_validate(new_quiz)

    @staticmethod
    async def get_quizzes(
        uow: IUnitOfWork,
        company_id: int,
        skip: int,
        limit: int,
        current_user_id: int,
        request_url: str,
    ) -> QuizzesListResponse:
        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id
            )

            total_quizzes = await uow.quizzes.count_all(company_id=company_id)
            quizzes = await uow.quizzes.find_all(
                skip=skip, limit=limit, company_id=company_id
            )
            total_pages = (total_quizzes + limit - 1) // limit
            current_page = (skip // limit) + 1

            base_url = request_url.split("?")[0]
            previous_page_url = (
                f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"
                if current_page > 1
                else None
            )
            next_page_url = (
                f"{base_url}?skip={skip + limit}&limit={limit}"
                if current_page < total_pages
                else None
            )

            return QuizzesListResponse(
                total_item=total_quizzes,
                total_page=total_pages,
                current_page=current_page,
                data=[QuizSchemaResponse.model_validate(quiz) for quiz in quizzes],
                pagination=PaginationLinks(
                    previous=previous_page_url, next=next_page_url
                ),
            )

    @staticmethod
    async def update_quiz(
        uow: IUnitOfWork,
        quiz_id: int,
        update_data: UpdateQuizRequest,
        current_user_id: int,
    ) -> QuizSchemaResponse:
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )
            updated_quiz = await uow.quizzes.edit_one(quiz_id, update_data.model_dump())
            return QuizSchemaResponse.model_validate(updated_quiz)

    @staticmethod
    async def delete_quiz(uow: IUnitOfWork, quiz_id: int, current_user_id: int) -> None:
        async with uow:
            quiz = await uow.quizzes.find_one(id=quiz_id)
            await CompanyService.check_company_permission(
                uow, quiz.company_id, current_user_id, is_admin=True
            )
            await uow.quizzes.delete_one(quiz_id)
