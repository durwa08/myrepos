"""
Test cases for ResultService.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    AttemptAccessDeniedException,
    AttemptNotFoundException,
    AttemptNotSubmittedException,
)
from app.services.result_service import ResultService

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
        "answers": {"q1": 2},
        "status": "submitted",
        "started_at": now,
        "submitted_at": now,
        "total_questions": 1,
        "correct_answers": 1,
        "percentage": 100.0,
        "passed": True,
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_get_result_success(mocker):
    """
    Test retrieving the result of a submitted attempt.
    """
    mocker.patch(
        "app.services.result_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(),
    )

    service = ResultService()
    result = await service.get_result(VALID_ID, student_id="student1")

    assert result.percentage == 100.0
    assert result.answer_breakdown[0].is_correct is True


@pytest.mark.asyncio
async def test_get_result_not_found(mocker):
    """
    Test retrieving a result fails when the attempt does not exist.
    """
    mocker.patch(
        "app.services.result_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = ResultService()

    with pytest.raises(AttemptNotFoundException):
        await service.get_result("missing_id", student_id="student1")


@pytest.mark.asyncio
async def test_get_result_not_submitted(mocker):
    """
    Test retrieving a result fails when the attempt isn't submitted yet.
    """
    mocker.patch(
        "app.services.result_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(status="in_progress"),
    )

    service = ResultService()

    with pytest.raises(AttemptNotSubmittedException):
        await service.get_result(VALID_ID, student_id="student1")


@pytest.mark.asyncio
async def test_get_result_access_denied(mocker):
    """
    Test retrieving a result fails for a non-owning student.
    """
    mocker.patch(
        "app.services.result_service.get_attempt_by_id",
        new_callable=AsyncMock,
        return_value=make_raw_attempt(student_id="other_student"),
    )

    service = ResultService()

    with pytest.raises(AttemptAccessDeniedException):
        await service.get_result(VALID_ID, student_id="student1")


@pytest.mark.asyncio
async def test_get_history(mocker):
    """
    Test retrieving a student's full result history.
    """
    mocker.patch(
        "app.services.result_service.list_submitted_attempts_by_student",
        new_callable=AsyncMock,
        return_value=[make_raw_attempt()],
    )

    service = ResultService()
    result = await service.get_history(student_id="student1")

    assert len(result) == 1
    assert result[0].percentage == 100.0


@pytest.mark.asyncio
async def test_get_admin_dashboard(mocker):
    """
    Test retrieving all submitted results for the admin dashboard.
    """
    mocker.patch(
        "app.services.result_service.list_all_submitted_attempts",
        new_callable=AsyncMock,
        return_value=[
            make_raw_attempt(student_id="student1"),
            make_raw_attempt(student_id="student2", correct_answers=0, percentage=0.0, passed=False),
        ],
    )

    service = ResultService()
    result = await service.get_admin_dashboard()

    assert len(result) == 2