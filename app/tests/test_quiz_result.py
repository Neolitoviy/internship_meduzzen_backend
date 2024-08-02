import json
from datetime import datetime
from unittest.mock import patch

import pytest
from faker import Faker

from app.schemas.analytics import CompanyMemberAverageScore, QuizTrend
from app.schemas.answer import AnswerSchemaResponse
from app.schemas.company_member import CompanyMemberResponse
from app.schemas.question import QuestionSchemaResponse
from app.schemas.quiz import QuizSchemaResponse
from app.schemas.quiz_result import QuizResultResponse, QuizVoteRequest, UserQuizVote
from app.services.quiz_result import QuizResultService

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
        answer_text=faker.word(),
        is_correct=True,
        question_id=1,
    )


@pytest.fixture
def mock_quiz_result():
    return QuizResultResponse(
        id=1,
        user_id=1,
        quiz_id=1,
        company_id=1,
        total_questions=10,
        total_answers=8,
        score=80.0,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_member():
    return CompanyMemberResponse(
        id=1,
        user_id=1,
        company_id=1,
        is_admin=True,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_last_attempt():
    return QuizResultResponse(
        id=1,
        user_id=1,
        quiz_id=1,
        company_id=1,
        total_questions=10,
        total_answers=8,
        score=80.0,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_vote():
    return UserQuizVote(
        user_id=1,
        company_id=1,
        quiz_id=1,
        question_id=1,
        question_text="Test question",
        answer_text="Test answer",
        is_correct=True,
        timestamp=1722032857.190859,
    )


@pytest.mark.asyncio
async def test_quiz_vote(uow, mock_quiz, mock_question, mock_answer, mock_quiz_result):
    vote_data = QuizVoteRequest(answers={1: 1})
    current_user_id = 1

    uow.quizzes.find_one.return_value = mock_quiz
    uow.questions.find_one.return_value = mock_question
    uow.answers.find_one.return_value = mock_answer
    uow.quiz_results.add_one.return_value = mock_quiz_result

    quiz_response = await QuizResultService.quiz_vote(
        uow, mock_quiz.company_id, mock_quiz.id, vote_data, current_user_id
    )

    assert quiz_response.score == mock_quiz_result.score
    assert uow.quiz_results.add_one.called


@pytest.mark.asyncio
async def test_get_user_average_score(uow, mock_quiz_result):
    user_id = 1
    company_id = 1
    current_user_id = 1

    uow.quiz_results.get_average_score.return_value = mock_quiz_result.score

    avg_score = await QuizResultService.get_user_average_score(
        uow, user_id, company_id, current_user_id
    )

    assert avg_score == mock_quiz_result.score
    assert uow.quiz_results.get_average_score.called


@pytest.mark.asyncio
async def test_get_company_average_score(uow, mock_quiz_result):
    user_id = 1
    company_id = 1
    current_user_id = 1

    uow.quiz_results.get_average_score.return_value = mock_quiz_result.score

    avg_score = await QuizResultService.get_company_average_score(
        uow, user_id, company_id, current_user_id
    )

    assert avg_score == mock_quiz_result.score
    assert uow.quiz_results.get_average_score.called


@pytest.mark.asyncio
async def test_get_user_quiz_scores(uow, mock_quiz_result, mock_quiz):
    user_id = 1
    skip = 0
    limit = 10

    uow.quiz_results.find_all.return_value = [mock_quiz_result]
    uow.quizzes.find_one.return_value = mock_quiz

    quiz_scores = await QuizResultService.get_user_quiz_scores(
        uow, user_id, skip, limit
    )

    assert len(quiz_scores) > 0
    assert quiz_scores[0].quiz_id == mock_quiz_result.quiz_id
    assert uow.quiz_results.find_all.called
    assert uow.quizzes.find_one.called


@pytest.mark.asyncio
async def test_get_user_last_quiz_attempts(uow, mock_quiz_result):
    user_id = 1
    skip = 0
    limit = 10

    uow.quiz_results.find_all.return_value = [mock_quiz_result]

    last_attempts = await QuizResultService.get_user_last_quiz_attempts(
        uow, user_id, skip, limit
    )

    assert len(last_attempts) > 0
    assert last_attempts[0].quiz_id == mock_quiz_result.quiz_id
    assert uow.quiz_results.find_all.called


@pytest.mark.asyncio
async def test_get_company_members_average_scores_over_time(uow, mock_quiz_result):
    company_id = 1
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 1, 1)
    current_user_id = 1
    skip = 0
    limit = 10

    member_scores = [
        CompanyMemberAverageScore(
            user_id=1,
            average_score=85.0,
            start_date=start_date,
            end_date=end_date,
        )
    ]

    uow.quiz_results.get_company_members_average_scores.return_value = member_scores

    scores = await QuizResultService.get_company_members_average_scores_over_time(
        uow, company_id, start_date, end_date, current_user_id, skip, limit
    )

    assert len(scores) > 0
    assert scores[0].user_id == member_scores[0].user_id
    assert uow.quiz_results.get_company_members_average_scores.called


@pytest.mark.asyncio
async def test_get_user_quiz_trends(uow, mock_quiz_result, mock_quiz):
    company_id = 1
    user_id = 1
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 1, 1)
    current_user_id = 1
    skip = 0
    limit = 10

    quiz_trends = [
        QuizTrend(
            quiz_id=1,
            quiz_title="Sample Quiz",
            average_score=90.0,
            start_date=start_date,
            end_date=end_date,
        )
    ]

    uow.quiz_results.get_quiz_trends_by_date_range.return_value = quiz_trends
    uow.quizzes.find_one.return_value = mock_quiz

    trends = await QuizResultService.get_user_quiz_trends(
        uow, company_id, user_id, start_date, end_date, current_user_id, skip, limit
    )

    assert len(trends) > 0
    assert trends[0].quiz_id == quiz_trends[0].quiz_id
    assert uow.quiz_results.get_quiz_trends_by_date_range.called
    assert uow.quizzes.find_one.called


@pytest.mark.asyncio
async def test_get_company_user_last_attempts(uow, mock_member, mock_last_attempt):
    company_id = 1
    requesting_user_id = 1
    skip = 0
    limit = 10

    uow.company_members.find_all.return_value = [mock_member]
    uow.quiz_results.find_last_attempt_with_filter.return_value = mock_last_attempt

    last_attempts = await QuizResultService.get_company_user_last_attempts(
        uow, company_id, requesting_user_id, skip, limit
    )

    assert len(last_attempts) > 0
    assert last_attempts[0].user_id == mock_member.user_id
    assert last_attempts[0].last_attempt == mock_last_attempt.created_at
    assert uow.company_members.find_all.called
    assert uow.quiz_results.find_last_attempt_with_filter.called


@pytest.mark.asyncio
@patch("app.services.quiz_result.get_redis_client")
async def test_save_quiz_vote_to_redis(
    mock_get_redis_client, mock_vote, mock_redis_client
):
    mock_get_redis_client.return_value = mock_redis_client

    await QuizResultService.save_quiz_vote_to_redis(mock_vote)

    mock_redis_client.setex.assert_called_once_with(
        f"quiz_vote:{mock_vote.user_id}:{mock_vote.company_id}:{mock_vote.quiz_id}:{mock_vote.question_id}",
        172800,
        json.dumps(mock_vote.dict()),
    )


@pytest.mark.asyncio
@patch("app.services.quiz_result.get_redis_client")
async def test_get_quiz_votes_from_redis(
    mock_get_redis_client, mock_vote, mock_redis_client, uow
):
    mock_get_redis_client.return_value = mock_redis_client
    mock_redis_client.keys.return_value = [
        f"quiz_vote:{mock_vote.user_id}:{mock_vote.company_id}:{mock_vote.quiz_id}:{mock_vote.question_id}"
    ]
    mock_redis_client.get.return_value = json.dumps(mock_vote.dict())

    uow.company_members.find_one_or_none.return_value = (
        True  # Mock the company_members method
    )

    quiz_votes = await QuizResultService.get_quiz_votes_from_redis(
        uow, 1, mock_vote.user_id, mock_vote.company_id, mock_vote.quiz_id
    )

    assert len(quiz_votes) == 1
    assert quiz_votes[0].user_id == mock_vote.user_id
    assert quiz_votes[0].company_id == mock_vote.company_id
    assert quiz_votes[0].quiz_id == mock_vote.quiz_id
    assert quiz_votes[0].question_id == mock_vote.question_id


@pytest.mark.asyncio
@patch("app.services.quiz_result.get_redis_client")
async def test_get_vote_redis(mock_get_redis_client, mock_vote, mock_redis_client, uow):
    mock_get_redis_client.return_value = mock_redis_client
    mock_redis_client.get.return_value = json.dumps(mock_vote.dict())

    uow.company_members.find_one_or_none.return_value = (
        True  # Mock the company_members method
    )

    vote = await QuizResultService.get_vote_redis(
        uow,
        1,
        mock_vote.user_id,
        mock_vote.company_id,
        mock_vote.quiz_id,
        mock_vote.question_id,
    )

    assert vote["user_id"] == mock_vote.user_id
    assert vote["company_id"] == mock_vote.company_id
    assert vote["quiz_id"] == mock_vote.quiz_id
    assert vote["question_id"] == mock_vote.question_id


@pytest.mark.asyncio
@patch("app.services.quiz_result.get_redis_client")
async def test_export_quiz_results_from_redis_to_csv(
    mock_get_redis_client, mock_vote, mock_redis_client, uow
):
    mock_get_redis_client.return_value = mock_redis_client
    mock_redis_client.keys.return_value = [
        f"quiz_vote:{mock_vote.user_id}:{mock_vote.company_id}:{mock_vote.quiz_id}:{mock_vote.question_id}"
    ]
    mock_redis_client.get.return_value = json.dumps(mock_vote.dict())

    uow.company_members.find_one_or_none.return_value = (
        True  # Mock the company_members method
    )

    csv_result = await QuizResultService.export_quiz_results_from_redis_to_csv(
        uow, 1, mock_vote.user_id, mock_vote.company_id, mock_vote.quiz_id
    )

    expected_csv = (
        "User ID,Company ID,Quiz ID,Question ID,Question Text,Answer Text,Is Correct,Timestamp\r\n"
        "1,1,1,1,Test question,Test answer,True,1722032857.190859\r\n"
    )
    assert csv_result == expected_csv


@pytest.mark.asyncio
@patch("app.services.quiz_result.get_redis_client")
async def test_export_quiz_results_from_redis_to_json(
    mock_get_redis_client, mock_vote, mock_redis_client, uow
):
    mock_get_redis_client.return_value = mock_redis_client
    mock_redis_client.keys.return_value = [
        f"quiz_vote:{mock_vote.user_id}:{mock_vote.company_id}:{mock_vote.quiz_id}:{mock_vote.question_id}"
    ]
    mock_redis_client.get.return_value = json.dumps(mock_vote.dict())

    uow.company_members.find_one_or_none.return_value = (
        True  # Mock the company_members method
    )

    json_result = await QuizResultService.export_quiz_results_from_redis_to_json(
        uow, 1, mock_vote.user_id, mock_vote.company_id, mock_vote.quiz_id
    )

    expected_json = json.dumps([mock_vote.dict()])
    assert json_result == expected_json
