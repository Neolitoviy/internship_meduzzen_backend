from datetime import datetime

import pytest
from faker import Faker

from app.schemas.company_member import CompanyMemberResponse
from app.schemas.question import AnswerSchemaCreate, QuestionSchemaCreate
from app.schemas.quiz import CreateQuizRequest, QuizSchemaResponse, UpdateQuizRequest
from app.services.quiz import QuizService

faker = Faker()


@pytest.fixture
def mock_quiz():
    title = faker.word()
    description = faker.text()
    return QuizSchemaResponse(
        id=1,
        title=title,
        description=description,
        frequency_in_days=7,
        company_id=1,
        user_id=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_create_quiz(uow, mock_quiz):
    question_data = QuestionSchemaCreate(
        question_text=faker.sentence(),
        answers=[
            AnswerSchemaCreate(answer_text=faker.word(), is_correct=True),
            AnswerSchemaCreate(answer_text=faker.word(), is_correct=False),
        ],
    )

    quiz_data = CreateQuizRequest(
        title=mock_quiz.title,
        description=mock_quiz.description,
        frequency_in_days=7,
        company_id=1,
        questions_data=[question_data, question_data],
    )
    current_user_id = 1

    uow.quizzes.add_one.return_value = mock_quiz
    uow.company_members.find_all.return_value = [
        CompanyMemberResponse(
            id=1,
            user_id=current_user_id,
            company_id=1,
            is_admin=True,
            created_at=datetime.utcnow(),
        )
    ]

    quiz_response = await QuizService.create_quiz(uow, quiz_data, current_user_id)

    assert quiz_response.title == quiz_data.title
    assert quiz_response.description == quiz_data.description
    assert quiz_response.company_id == quiz_data.company_id
    assert uow.quizzes.add_one.called
    assert uow.notifications.add_one.called


@pytest.mark.asyncio
async def test_get_quizzes(uow, mock_quiz):
    company_id = 1
    skip = 0
    limit = 10
    current_user_id = 1
    request_url = "http://test.com/quizzes"

    uow.quizzes.count_all.return_value = 1
    uow.quizzes.find_all.return_value = [mock_quiz]

    quizzes_list_response = await QuizService.get_quizzes(
        uow, company_id, skip, limit, current_user_id, request_url
    )

    assert quizzes_list_response.items[0].title == mock_quiz.title
    assert quizzes_list_response.items[0].description == mock_quiz.description
    assert quizzes_list_response.total_pages == 1
    assert quizzes_list_response.current_page == 1
    assert uow.quizzes.find_all.called


@pytest.mark.asyncio
async def test_update_quiz(uow, mock_quiz):
    quiz_id = 1
    current_user_id = 1
    update_data = UpdateQuizRequest(
        title="Updated Title", description="Updated Description", frequency_in_days=14
    )

    updated_mock_quiz = QuizSchemaResponse(
        id=1,
        title=update_data.title,
        description=update_data.description,
        frequency_in_days=update_data.frequency_in_days,
        company_id=mock_quiz.company_id,
        user_id=mock_quiz.user_id,
    )

    uow.quizzes.find_one.return_value = mock_quiz
    uow.quizzes.edit_one.return_value = updated_mock_quiz

    quiz_response = await QuizService.update_quiz(
        uow, quiz_id, update_data, current_user_id
    )

    assert quiz_response.title == update_data.title
    assert quiz_response.description == update_data.description
    assert quiz_response.frequency_in_days == update_data.frequency_in_days
    assert uow.quizzes.edit_one.called


@pytest.mark.asyncio
async def test_delete_quiz(uow, mock_quiz):
    quiz_id = 1
    current_user_id = 1

    uow.quizzes.find_one.return_value = mock_quiz

    await QuizService.delete_quiz(uow, quiz_id, current_user_id)

    assert uow.quizzes.delete_one.called
