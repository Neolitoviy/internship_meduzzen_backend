import pytest
from app.services.quiz import QuizService
from app.schemas.quiz import CreateQuizRequest, QuizSchemaResponse
from app.utils.unitofwork import IUnitOfWork
from app.core.exceptions import PermissionDenied


async def test_create_quiz(uow: IUnitOfWork, current_user_id: int):
    quiz_data = CreateQuizRequest(
        title="Test Quiz",
        description="This is a test quiz.",
        frequency_in_days=7,
        company_id=1,
        questions_data=[
            {
                "question_text": "Question 1",
                "answers": [
                    {"answer_text": "Answer 1", "is_correct": True},
                    {"answer_text": "Answer 2", "is_correct": False}
                ]
            },
            {
                "question_text": "Question 2",
                "answers": [
                    {"answer_text": "Answer 1", "is_correct": True},
                    {"answer_text": "Answer 2", "is_correct": False}
                ]
            }
        ]
    )

    service = QuizService()

    # Create a quiz
    quiz_response = await service.create_quiz(uow, quiz_data, current_user_id)

    assert isinstance(quiz_response, QuizSchemaResponse)
    assert quiz_response.title == "Test Quiz"
    assert len(quiz_response.questions) == 2


async def test_get_quizzes(uow: IUnitOfWork, current_user_id: int):
    service = QuizService()
    company_id = 1
    skip = 0
    limit = 10

    quizzes_response = await service.get_quizzes(uow, company_id, skip, limit, current_user_id)

    assert quizzes_response.total_pages > 0
    assert quizzes_response.current_page == 1


async def test_permission_denied_create_quiz(uow: IUnitOfWork, current_user_id: int):
    quiz_data = CreateQuizRequest(
        title="Test Quiz",
        description="This is a test quiz.",
        frequency_in_days=7,
        company_id=1,
        questions_data=[
            {
                "question_text": "Question 1",
                "answers": [
                    {"answer_text": "Answer 1", "is_correct": True},
                    {"answer_text": "Answer 2", "is_correct": False}
                ]
            }
        ]
    )

    service = QuizService()

    # Simulate permission denied
    with pytest.raises(PermissionDenied):
        await service.create_quiz(uow, quiz_data, current_user_id + 1)
