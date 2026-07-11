"""
Test cases for AttemptService.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    AttemptAccessDeniedException,
    AttemptAlreadySubmittedException,
    AttemptExpiredException,
    AttemptNotFoundException,
    AttemptNotSubmittedException,
    InvalidAttemptAnswerException,
    MaxAttemptsReachedException,
    QuizNotFoundException,
)
from app.schemas.attempt_schema import AnswerSaveRequest
from app.services.attempt_service import AttemptService

VALID_ID = "6a45f4149915f959917d382b"


def make_raw_attempt(**overrides):
    """
    Build a raw attempt document dict with sensible defaults.
    """
    now = datetime.now(timezone.utc)
    base = {
        "_id": VALID_ID,
        "quiz_id": "quiz1",
        "student_id": "student1",
        "attempt_number": 1,
        "questions_snapshot": [
            {
                "question_id": "q1",
                "question_text": "What is 2+2?",
                "question_type": "mcq",
                "options": ["2", "3", "4", "5"],
                "correct_answer_index": 2,
                "difficulty": "easy",
                "tags": [],
            }
        ],
        "answers": {},
        "status": "in_progress",
        "started_at": now,
        "expires_at": now + timedelta(minutes=30),
        "submitted_at": None,
        "total_questions": None,
        "correct_answers": None,
        "percentage": None,
        "passed": None,
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_start_attempt_success(mocker):
    """
    Test starting a new attempt when no active attempt exists.
    """
    mocker.patch(
        "app.services.attempt_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "quiz1",
            "time_limit_minutes": 30,
            "pass_percentage": 40.0,
        },
    )
    mocker.patch(
        "app.services.attempt_service.get_active_attempt",
        new_callable=AsyncMock,
        return_value=None,
    )
    mocker.patch(
        "app.services.attempt_service.count_attempts_by_student_and_quiz",
        new_callable=AsyncMock,
        return_value=0,
    )
    mocker.patch(
        "app.services.attempt_service.list_questions_by_quiz",
        new_callable=AsyncMock,
        return_value=[
            {
                "_id": "q1",
                "question_text": "What is 2+2?",
                "question_type": "mcq",
                "options": ["2", "3", "4", "5"],
                "correct_answer_index": 2,
                "difficulty": "easy",
                "tags": [],
            }
        ],
    )
    mocker.patch(
        "app.services.attempt_service.create_attempt",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(),
    )

    service = AttemptService()
    response = await service.start_attempt("quiz1", student_id="student1")

    assert response.attempt_number == 1
    assert response.status == "in_progress"


@pytest.mark.asyncio
async def test_start_attempt_quiz_not_found(mocker):
    """
    Test starting an attempt fails when the quiz doesn't exist.
    """
    mocker.patch(
        "app.services.attempt_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = AttemptService()

    with pytest.raises(QuizNotFoundException):
        await service.start_attempt("missing_quiz", student_id="student1")


@pytest.mark.asyncio
async def test_start_attempt_auto_resumes_active_attempt(mocker):
    """
    Test that starting an attempt returns the existing unexpired
    in-progress attempt instead of creating a new one.
    """
    mocker.patch(
        "app.services.attempt_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={"_id": "quiz1", "time_limit_minutes": 30},
    )
    mocker.patch(
        "app.services.attempt_service.get_active_attempt",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(),
    )
    mock_create = mocker.patch(
        "app.services.attempt_service.create_attempt",
        new_callable=AsyncMock,
    )

    service = AttemptService()
    response = await service.start_attempt("quiz1", student_id="student1")

    assert response.id == VALID_ID
    mock_create.assert_not_awaited()


@pytest.mark.asyncio
async def test_start_attempt_max_attempts_reached(mocker):
    """
    Test starting an attempt fails when the max attempts limit is hit.
    """
    mocker.patch(
        "app.services.attempt_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={"_id": "quiz1", "time_limit_minutes": 30},
    )
    mocker.patch(
        "app.services.attempt_service.get_active_attempt",
        new_callable=AsyncMock,
        return_value=None,
    )
    mocker.patch(
        "app.services.attempt_service.count_attempts_by_student_and_quiz",
        new_callable=AsyncMock,
        return_value=3,
    )

    service = AttemptService()

    with pytest.raises(MaxAttemptsReachedException):
        await service.start_attempt("quiz1", student_id="student1")


@pytest.mark.asyncio
async def test_resume_attempt_success(mocker):
    """
    Test resuming a valid, unexpired, owned attempt.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(),
    )

    service = AttemptService()
    response = await service.resume_attempt(VALID_ID, student_id="student1")

    assert response.id == VALID_ID


@pytest.mark.asyncio
async def test_resume_attempt_not_found(mocker):
    """
    Test resuming fails when the attempt does not exist.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = AttemptService()

    with pytest.raises(AttemptNotFoundException):
        await service.resume_attempt("missing_id", student_id="student1")


@pytest.mark.asyncio
async def test_resume_attempt_access_denied(mocker):
    """
    Test resuming fails when the attempt belongs to a different student.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(student_id="other_student"),
    )

    service = AttemptService()

    with pytest.raises(AttemptAccessDeniedException):
        await service.resume_attempt(VALID_ID, student_id="student1")


@pytest.mark.asyncio
async def test_resume_attempt_expired(mocker):
    """
    Test resuming fails and marks the attempt expired when the time
    limit has passed.
    """
    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(expires_at=past_time),
    )
    mock_mark_expired = mocker.patch(
        "app.services.attempt_service.mark_attempt_expired",
        new_callable=AsyncMock,
    )

    service = AttemptService()

    with pytest.raises(AttemptExpiredException):
        await service.resume_attempt(VALID_ID, student_id="student1")

    mock_mark_expired.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_answer_success(mocker):
    """
    Test saving a valid answer for an in-progress attempt.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(),
    )
    mocker.patch(
        "app.services.attempt_service.save_answer",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(answers={"q1": 2}),
    )

    service = AttemptService()
    request = AnswerSaveRequest(question_id="q1", answer_index=2)
    response = await service.save_answer(VALID_ID, request, student_id="student1")

    assert response.answers == {"q1": 2}


@pytest.mark.asyncio
async def test_save_answer_invalid_question(mocker):
    """
    Test saving an answer fails when the question doesn't belong to
    the attempt's snapshot.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(),
    )

    service = AttemptService()
    request = AnswerSaveRequest(question_id="not_in_snapshot", answer_index=0)

    with pytest.raises(InvalidAttemptAnswerException):
        await service.save_answer(VALID_ID, request, student_id="student1")


@pytest.mark.asyncio
async def test_save_answer_invalid_index(mocker):
    """
    Test saving an answer fails when the index is out of range.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(),
    )

    service = AttemptService()
    request = AnswerSaveRequest(question_id="q1", answer_index=99)

    with pytest.raises(InvalidAttemptAnswerException):
        await service.save_answer(VALID_ID, request, student_id="student1")


@pytest.mark.asyncio
async def test_submit_attempt_success(mocker):
    """
    Test submitting an attempt computes and stores the score.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(answers={"q1": 2}),
    )
    mocker.patch(
        "app.services.attempt_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={"pass_percentage": 40.0},
    )
    mocker.patch(
        "app.services.attempt_service.submit_attempt",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(
            status="submitted",
            submitted_at=datetime.now(timezone.utc),
            total_questions=1,
            correct_answers=1,
            percentage=100.0,
            passed=True,
        ),
    )

    service = AttemptService()
    response = await service.submit_attempt(VALID_ID, student_id="student1")

    assert response.status == "submitted"
    assert response.percentage == 100.0
    assert response.passed is True
    assert response.answer_breakdown[0].is_correct is True


@pytest.mark.asyncio
async def test_submit_attempt_wrong_answer(mocker):
    """
    Test that an incorrect answer results in a failing score.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(answers={"q1": 0}),
    )
    mocker.patch(
        "app.services.attempt_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={"pass_percentage": 40.0},
    )
    mocker.patch(
        "app.services.attempt_service.submit_attempt",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(
            status="submitted",
            submitted_at=datetime.now(timezone.utc),
            total_questions=1,
            correct_answers=0,
            percentage=0.0,
            passed=False,
        ),
    )

    service = AttemptService()
    response = await service.submit_attempt(VALID_ID, student_id="student1")

    assert response.percentage == 0.0
    assert response.passed is False


@pytest.mark.asyncio
async def test_submit_attempt_already_submitted(mocker):
    """
    Test submitting fails when the attempt is already submitted.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(status="submitted"),
    )

    service = AttemptService()

    with pytest.raises(AttemptAlreadySubmittedException):
        await service.submit_attempt(VALID_ID, student_id="student1")


@pytest.mark.asyncio
async def test_submit_attempt_allows_expired(mocker):
    """
    Test that an expired (but not yet submitted) attempt can still be
    submitted, per the auto-submit-on-expiry behavior.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(status="expired", answers={"q1": 2}),
    )
    mocker.patch(
        "app.services.attempt_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={"pass_percentage": 40.0},
    )
    mocker.patch(
        "app.services.attempt_service.submit_attempt",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(
            status="submitted",
            submitted_at=datetime.now(timezone.utc),
            total_questions=1,
            correct_answers=1,
            percentage=100.0,
            passed=True,
        ),
    )

    service = AttemptService()
    response = await service.submit_attempt(VALID_ID, student_id="student1")

    assert response.status == "submitted"


@pytest.mark.asyncio
async def test_get_result_success(mocker):
    """
    Test retrieving the result of a submitted attempt.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(
            status="submitted",
            answers={"q1": 2},
            submitted_at=datetime.now(timezone.utc),
            total_questions=1,
            correct_answers=1,
            percentage=100.0,
            passed=True,
        ),
    )

    service = AttemptService()
    result = await service.get_result(VALID_ID, student_id="student1")

    assert result.percentage == 100.0
    assert result.answer_breakdown[0].is_correct is True


@pytest.mark.asyncio
async def test_get_result_not_submitted(mocker):
    """
    Test retrieving a result fails when the attempt isn't submitted yet.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(status="in_progress"),
    )

    service = AttemptService()

    with pytest.raises(AttemptNotSubmittedException):
        await service.get_result(VALID_ID, student_id="student1")


@pytest.mark.asyncio
async def test_get_result_access_denied(mocker):
    """
    Test retrieving a result fails for a non-owning student.
    """
    mocker.patch(
        "app.services.attempt_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(
            status="submitted", student_id="other_student"
        ),
    )

    service = AttemptService()

    with pytest.raises(AttemptAccessDeniedException):
        await service.get_result(VALID_ID, student_id="student1")


@pytest.mark.asyncio
async def test_get_history(mocker):
    """
    Test retrieving a student's full result history.
    """
    mocker.patch(
        "app.services.attempt_service.list_submitted_attempts_by_student",
        new_callable=AsyncMock,
        return_value=[
            make_raw_attempt(
                status="submitted",
                submitted_at=datetime.now(timezone.utc),
                total_questions=1,
                correct_answers=1,
                percentage=100.0,
                passed=True,
            )
        ],
    )

    service = AttemptService()
    result = await service.get_history(student_id="student1")

    assert len(result) == 1
    assert result[0].percentage == 100.0


@pytest.mark.asyncio
async def test_get_admin_dashboard(mocker):
    """
    Test retrieving all submitted results for the admin dashboard.
    """
    mocker.patch(
        "app.services.attempt_service.list_all_submitted_attempts",
        new_callable=AsyncMock,
        return_value=[
            make_raw_attempt(
                status="submitted",
                student_id="student1",
                submitted_at=datetime.now(timezone.utc),
                total_questions=1,
                correct_answers=1,
                percentage=100.0,
                passed=True,
            ),
            make_raw_attempt(
                status="submitted",
                student_id="student2",
                submitted_at=datetime.now(timezone.utc),
                total_questions=1,
                correct_answers=0,
                percentage=0.0,
                passed=False,
            ),
        ],
    )

    service = AttemptService()
    result = await service.get_admin_dashboard()

    assert len(result) == 2