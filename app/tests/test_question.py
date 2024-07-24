import pytest

from app.core.exceptions import PermissionDenied
from app.schemas.question import QuestionSchemaCreate, QuestionSchemaResponse
from app.services.question import QuestionService
from app.utils.unitofwork import IUnitOfWork


async def test_create_question(uow: IUnitOfWork, current_user_id: int):
    question_data = QuestionSchemaCreate(
        quiz_id=1,
        question_text="Question 1",
        answers=[
            {"answer_text": "Answer 1", "is_correct": True},
            {"answer_text": "Answer 2", "is_correct": False},
        ],
    )

    service = QuestionService()

    # Create a question
    question_response = await service.create_question(
        uow, 1, question_data, current_user_id
    )

    assert isinstance(question_response, QuestionSchemaResponse)
    assert question_response.question_text == "Question 1"


async def test_get_questions_by_quiz_id(uow: IUnitOfWork, current_user_id: int):
    service = QuestionService()
    quiz_id = 1
    skip = 0
    limit = 10

    questions_response = await service.get_questions_by_quiz_id(
        uow, quiz_id, current_user_id, skip, limit
    )

    assert len(questions_response) > 0


async def test_permission_denied_create_question(
    uow: IUnitOfWork, current_user_id: int
):
    question_data = QuestionSchemaCreate(
        quiz_id=1,
        question_text="Question 1",
        answers=[
            {"answer_text": "Answer 1", "is_correct": True},
            {"answer_text": "Answer 2", "is_correct": False},
        ],
    )

    service = QuestionService()

    # Simulate permission denied
    with pytest.raises(PermissionDenied):
        await service.create_question(uow, 1, question_data, current_user_id + 1)
