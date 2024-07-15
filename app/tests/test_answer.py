import pytest
from app.services.answer import AnswerService
from app.schemas.answer import AnswerSchemaCreate, AnswerSchemaResponse
from app.utils.unitofwork import IUnitOfWork
from app.core.exceptions import PermissionDenied


async def test_create_answer(uow: IUnitOfWork, current_user_id: int):
    answer_data = AnswerSchemaCreate(
        question_id=1,
        answer_text="Answer 1",
        is_correct=True
    )

    service = AnswerService()

    # Create an answer
    answer_response = await service.create_answer(uow, 1, answer_data, current_user_id)

    assert isinstance(answer_response, AnswerSchemaResponse)
    assert answer_response.answer_text == "Answer 1"


async def test_get_answers_by_question_id(uow: IUnitOfWork, current_user_id: int):
    service = AnswerService()
    question_id = 1
    skip = 0
    limit = 10

    answers_response = await service.get_answers_by_question_id(uow, question_id, current_user_id, skip, limit)

    assert len(answers_response) > 0


async def test_permission_denied_create_answer(uow: IUnitOfWork, current_user_id: int):
    answer_data = AnswerSchemaCreate(
        question_id=1,
        answer_text="Answer 1",
        is_correct=True
    )

    service = AnswerService()

    # Simulate permission denied
    with pytest.raises(PermissionDenied):
        await service.create_answer(uow, 1, answer_data, current_user_id + 1)
