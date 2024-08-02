import pytest
from faker import Faker

from app.core.exceptions import PermissionDenied
from app.schemas.answer import (
    AnswerSchemaCreate,
    AnswerSchemaResponse,
    AnswerSchemaUpdate,
)
from app.schemas.question import QuestionSchemaResponse
from app.schemas.quiz import QuizSchemaResponse
from app.services.answer import AnswerService

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
def mock_question():
    return QuestionSchemaResponse(
        id=1,
        quiz_id=1,
        question_text=faker.sentence(),
    )


@pytest.fixture
def mock_answer():
    return AnswerSchemaResponse(
        id=1,
        answer_text="through",  # Use the same word as in the assertion
        is_correct=True,
        question_id=1,
    )


@pytest.mark.asyncio
async def test_create_answer(uow, mock_quiz, mock_question, mock_answer):
    answer_data = AnswerSchemaCreate(
        answer_text="through",  # Use the same word as in mock_answer
        is_correct=True,
    )
    current_user_id = 1

    uow.questions.find_one.return_value = mock_question
    uow.quizzes.find_one.return_value = mock_quiz
    uow.answers.add_one.return_value = mock_answer

    answer_response = await AnswerService.create_answer(
        uow, mock_question.id, answer_data, current_user_id
    )

    assert answer_response.answer_text == answer_data.answer_text
    assert answer_response.is_correct == answer_data.is_correct


@pytest.mark.asyncio
async def test_update_answer(uow, mock_quiz, mock_question, mock_answer):
    answer_data = AnswerSchemaUpdate(
        answer_text="Updated Answer",
        is_correct=False,
    )
    updated_mock_answer = AnswerSchemaResponse(
        id=mock_answer.id,
        answer_text=answer_data.answer_text,
        is_correct=answer_data.is_correct,
        question_id=mock_answer.question_id,
    )
    current_user_id = 1

    uow.answers.find_one.return_value = mock_answer
    uow.questions.find_one.return_value = mock_question
    uow.quizzes.find_one.return_value = mock_quiz
    uow.answers.edit_one.return_value = updated_mock_answer

    answer_response = await AnswerService.update_answer(
        uow, mock_answer.id, answer_data, current_user_id
    )

    assert answer_response.answer_text == answer_data.answer_text
    assert answer_response.is_correct == answer_data.is_correct


@pytest.mark.asyncio
async def test_delete_answer(uow, mock_quiz, mock_question, mock_answer):
    current_user_id = 1

    uow.answers.find_one.return_value = mock_answer
    uow.questions.find_one.return_value = mock_question
    uow.quizzes.find_one.return_value = mock_quiz
    uow.answers.count_all.return_value = 3  # More than MIN_ANSWERS

    await AnswerService.delete_answer(uow, mock_answer.id, current_user_id)

    assert uow.answers.delete_one.called


@pytest.mark.asyncio
async def test_delete_answer_min_answers(uow, mock_quiz, mock_question, mock_answer):
    current_user_id = 1

    uow.answers.find_one.return_value = mock_answer
    uow.questions.find_one.return_value = mock_question
    uow.quizzes.find_one.return_value = mock_quiz
    uow.answers.count_all.return_value = 2  # Equal to MIN_ANSWERS

    with pytest.raises(PermissionDenied):
        await AnswerService.delete_answer(uow, mock_answer.id, current_user_id)


@pytest.mark.asyncio
async def test_get_answers_by_question_id(uow, mock_quiz, mock_question, mock_answer):
    current_user_id = 1

    uow.questions.find_one.return_value = mock_question
    uow.quizzes.find_one.return_value = mock_quiz
    uow.answers.find_all.return_value = [mock_answer]

    answers_response = await AnswerService.get_answers_by_question_id(
        uow, mock_question.id, current_user_id, 0, 10
    )

    assert len(answers_response) == 1
    assert answers_response[0].answer_text == mock_answer.answer_text
