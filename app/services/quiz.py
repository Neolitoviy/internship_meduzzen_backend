import os

import aiofiles
from fastapi import UploadFile

from app.core.exceptions import BadRequest
from app.schemas.answer import AnswerSchemaUpdate
from app.schemas.notification import NotificationCreate
from app.schemas.question import UpdateQuestionRequest
from app.schemas.quiz import (
    CreateQuizRequest,
    QuizSchemaResponse,
    QuizzesListResponse,
    UpdateQuizRequest,
)
from app.services.answer import AnswerService
from app.services.company import CompanyService
from app.services.question import QuestionService
from app.utils.pagination import paginate
from app.utils.parse_excel import parse_excel
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

            # Send notifications to company members
            company_members = await uow.company_members.find_abs_all(
                company_id=quiz_data.company_id
            )
            for member in company_members:
                notification = NotificationCreate(
                    user_id=member.user_id,
                    quiz_id=new_quiz.id,
                    message=f"A new quiz '{new_quiz.title}' has been created. You are invited to participate.",
                )
                await uow.notifications.add_one(notification.model_dump())

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

            quizzes_response = [
                QuizSchemaResponse.model_validate(quiz) for quiz in quizzes
            ]
            pagination_response = paginate(
                items=quizzes_response,
                total_items=total_quizzes,
                skip=skip,
                limit=limit,
                request_url=request_url,
            )

            return QuizzesListResponse(
                total_pages=pagination_response.total_pages,
                current_page=pagination_response.current_page,
                items=pagination_response.items,
                pagination=pagination_response.pagination,
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

    @staticmethod
    async def import_quizzes(
        uow: IUnitOfWork, file: UploadFile, current_user_id: int, company_id: int
    ):
        os.makedirs("temp", exist_ok=True)

        file_location = f"temp/{file.filename}"
        async with aiofiles.open(file_location, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        quizzes_data = parse_excel(file_location)
        os.remove(file_location)

        created_quizzes = []
        updated_quizzes = []

        async with uow:
            await CompanyService.check_company_permission(
                uow, company_id, current_user_id, is_admin=True
            )

            for quiz_data in quizzes_data:
                quiz = await uow.quizzes.find_one_or_none(
                    title=quiz_data.title, company_id=company_id
                )
                if quiz:
                    updated_quizzes.append(quiz_data.title)
                    await QuizService.update_existing_quiz(
                        uow, quiz, quiz_data, current_user_id
                    )
                else:
                    created_quizzes.append(quiz_data.title)
                    await QuizService.create_quiz(uow, quiz_data, current_user_id)

        return {
            "status": "Quizzes import completed",
            "created_quizzes": created_quizzes,
            "updated_quizzes": updated_quizzes,
        }

    @staticmethod
    async def update_existing_quiz(
        uow: IUnitOfWork, quiz, quiz_data: CreateQuizRequest, current_user_id: int
    ):
        update_quiz_data = UpdateQuizRequest(
            title=quiz_data.title,
            description=quiz_data.description,
            frequency_in_days=quiz_data.frequency_in_days,
        )
        await QuizService.update_quiz(uow, quiz.id, update_quiz_data, current_user_id)

        for question_data in quiz_data.questions_data:
            question = await uow.questions.find_one(
                question_text=question_data.question_text, quiz_id=quiz.id
            )
            if not question:
                await QuestionService.create_question(
                    uow, quiz.id, question_data, current_user_id
                )
            else:
                update_question_data = UpdateQuestionRequest(
                    question_text=question_data.question_text,
                )
                await QuestionService.update_question(
                    uow, question.id, update_question_data, current_user_id
                )
                for answer_data in question_data.answers:
                    answer = await uow.answers.find_one(
                        answer_text=answer_data.answer_text,
                        question_id=question.id,
                    )
                    if not answer:
                        await AnswerService.create_answer(
                            uow, question.id, answer_data, current_user_id
                        )
                    else:
                        update_answer_data = AnswerSchemaUpdate(
                            answer_text=answer_data.answer_text,
                            is_correct=answer_data.is_correct,
                        )
                        await AnswerService.update_answer(
                            uow, answer.id, update_answer_data, current_user_id
                        )

    @staticmethod
    async def validate_file_type(file: UploadFile):
        if not file.filename.endswith((".xlsx", ".xls")):
            raise BadRequest("Invalid file type. Please upload an Excel file.")
