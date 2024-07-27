from datetime import datetime

import pytest
from faker import Faker

from app.core.exceptions import PermissionDenied
from app.schemas.answer import AnswerSchemaCreate
from app.schemas.question import (
    QuestionSchemaCreate,
    QuestionSchemaResponse,
    UpdateQuestionRequest,
)
from app.schemas.quiz import QuizSchemaResponse
from app.services.question import QuestionService

faker = Faker()


@pytest.fixture
def mock_quiz():
    return QuizSchemaResponse(
        id=1,
        title=faker.word(),
        description=faker.text(),
        frequency_in_days=7,
        company_id=1,
        user_id=1,
    )


@pytest.fixture
def question_data():
    return QuestionSchemaCreate(
        question_text=faker.sentence(),
        answers=[
            AnswerSchemaCreate(answer_text=faker.word(), is_correct=True),
            AnswerSchemaCreate(answer_text=faker.word(), is_correct=False),
        ],
    )


@pytest.fixture
def mock_question(question_data):
    return QuestionSchemaResponse(
        id=1,
        question_text=question_data.question_text,
        quiz_id=1,
    )


@pytest.fixture
def mock_answer():
    return {
        "id": 1,
        "answer_text": faker.word(),
        "is_correct": True,
        "question_id": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.mark.asyncio
async def test_create_question(
    uow, mock_quiz, mock_question, mock_answer, question_data
):
    uow.quizzes.find_one.return_value = mock_quiz
    uow.questions.add_one.return_value = mock_question
    uow.answers.add_one.return_value = mock_answer

    question_response = await QuestionService.create_question(
        uow, mock_quiz.id, question_data, mock_quiz.user_id
    )

    assert question_response.question_text == question_data.question_text
    assert uow.quizzes.find_one.called
    assert uow.questions.add_one.called
    assert uow.answers.add_one.called


@pytest.mark.asyncio
async def test_update_question(uow, mock_question, mock_quiz):
    question_id = mock_question.id
    current_user_id = 1
    update_data = UpdateQuestionRequest(
        question_text="Updated Question",
    )

    updated_mock_question = QuestionSchemaResponse(
        id=mock_question.id,
        question_text=update_data.question_text,
        quiz_id=mock_question.quiz_id,
    )

    uow.questions.find_one.return_value = mock_question
    uow.quizzes.find_one.return_value = mock_quiz
    uow.questions.edit_one.return_value = updated_mock_question

    question_response = await QuestionService.update_question(
        uow, question_id, update_data, current_user_id
    )

    assert question_response.question_text == update_data.question_text
    assert uow.questions.find_one.called
    assert uow.questions.edit_one.called


@pytest.mark.asyncio
async def test_delete_question(uow, mock_question, mock_quiz):
    question_id = mock_question.id
    current_user_id = 1

    uow.questions.find_one.return_value = mock_question
    uow.quizzes.find_one.return_value = mock_quiz
    uow.questions.count_all.return_value = 3

    await QuestionService.delete_question(uow, question_id, current_user_id)

    assert uow.questions.find_one.called
    assert uow.questions.delete_one.called


@pytest.mark.asyncio
async def test_get_questions_by_quiz_id(uow, mock_question):
    quiz_id = mock_question.quiz_id
    current_user_id = 1
    questions = [mock_question]

    uow.quizzes.find_one.return_value = QuizSchemaResponse(
        id=quiz_id,
        title=faker.word(),
        description=faker.text(),
        frequency_in_days=7,
        company_id=1,
        user_id=1,
    )
    uow.questions.find_all.return_value = questions

    questions_response = await QuestionService.get_questions_by_quiz_id(
        uow, quiz_id, current_user_id, skip=0, limit=10
    )

    assert len(questions_response) == len(questions)
    assert uow.quizzes.find_one.called
    assert uow.questions.find_all.called


@pytest.mark.asyncio
async def test_check_min_questions(uow):
    quiz_id = 1
    uow.questions.count_all.return_value = 1

    with pytest.raises(PermissionDenied):
        await QuestionService.check_min_questions(uow, quiz_id)

    assert uow.questions.count_all.called
