"""
Test cases for quiz attempt request/response schemas.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.attempt_schema import (
    AnswerSaveRequest,
    AttemptResponse,
    QuestionSnapshotResponse,
    SubmitAttemptResponse,
)


def test_answer_save_request_valid():
    """
    Test a valid answer save request passes validation.
    """
    request = AnswerSaveRequest(question_id="q1", answer_index=2)
    assert request.question_id == "q1"
    assert request.answer_index == 2


def test_answer_save_request_negative_index_invalid():
    """
    Test answer save request fails when answer_index is negative.
    """
    with pytest.raises(ValidationError):
        AnswerSaveRequest(question_id="q1", answer_index=-1)


def test_question_snapshot_response_excludes_correct_answer():
    """
    Test that the snapshot response has no correct_answer_index field.
    """
    snapshot = QuestionSnapshotResponse(
        question_id="q1",
        question_text="What is 2+2?",
        question_type="mcq",
        options=["3", "4", "5", "6"],
        difficulty="easy",
        tags=["math"],
    )
    assert not hasattr(snapshot, "correct_answer_index")


def test_attempt_response_defaults_answers_to_empty_dict():
    """
    Test that AttemptResponse defaults answers to an empty dict.
    """
    response = AttemptResponse(
        id="1",
        quiz_id="q1",
        attempt_number=1,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        questions=[],
    )
    assert response.answers == {}


def test_attempt_response_with_answers():
    """
    Test that AttemptResponse correctly holds saved answers.
    """
    response = AttemptResponse(
        id="1",
        quiz_id="q1",
        attempt_number=1,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        questions=[],
        answers={"q1": 2},
    )
    assert response.answers == {"q1": 2}


def test_submit_attempt_response_valid():
    """
    Test a valid submit attempt response.
    """
    now = datetime.now(timezone.utc)
    response = SubmitAttemptResponse(
        id="1",
        quiz_id="q1",
        attempt_number=1,
        status="submitted",
        submitted_at=now,
        total_questions=2,
        correct_answers=1,
        percentage=50.0,
        passed=True,
    )
    assert response.percentage == 50.0
    assert response.passed is True