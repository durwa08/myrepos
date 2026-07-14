"""
Test cases for quiz attempt routes.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

from app.main import app
from app.middleware.auth_middleware import require_student
from app.schemas.attempt_schema import (
    AttemptResponse,
    QuestionSnapshotResponse,
    SubmitAttemptResponse,
)

NOW = datetime.now(timezone.utc)


def make_attempt_response():
    """
    Build a sample AttemptResponse for mocking service return values.
    """
    return AttemptResponse(
        id="1",
        quiz_id="quiz1",
        attempt_number=1,
        status="in_progress",
        started_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
        questions=[
            QuestionSnapshotResponse(
                question_id="q1",
                question_text="What is 2+2?",
                question_type="mcq",
                options=["2", "3", "4", "5"],
                difficulty="easy",
                tags=[],
            )
        ],
        answers={},
    )


def make_submit_response():
    """
    Build a sample SubmitAttemptResponse for mocking service return values.
    """
    return SubmitAttemptResponse(
        id="1",
        quiz_id="quiz1",
        attempt_number=1,
        status="submitted",
        submitted_at=NOW,
        total_questions=1,
        correct_answers=1,
        percentage=100.0,
        passed=True,
    )


def test_start_attempt_route_as_student(client, mocker):
    """
    Test the start attempt endpoint returns 201 for a student.
    """
    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.start_attempt",
        new=AsyncMock(return_value=make_attempt_response()),
    )

    response = client.post(
        "/attempts/start/quiz1", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 201
    assert response.json()["attempt_number"] == 1

    app.dependency_overrides.clear()


def test_start_attempt_route_without_student_token(client):
    """
    Test the start attempt endpoint returns 401/403 without a student token.
    """
    response = client.post("/attempts/start/quiz1")

    assert response.status_code in (401, 403)


def test_save_answer_route(client, mocker):
    """
    Test the save answer endpoint returns 200 with updated answers.
    """
    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    updated_response = make_attempt_response()
    updated_response.answers = {"q1": 2}

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.save_answer",
        new=AsyncMock(return_value=updated_response),
    )

    response = client.patch(
        "/attempts/1/answers",
        json={"question_id": "q1", "answer_index": 2},
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 200
    assert response.json()["answers"] == {"q1": 2}

    app.dependency_overrides.clear()


def test_submit_attempt_route(client, mocker):
    """
    Test the submit attempt endpoint returns 200 with the score summary.
    """
    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.submit_attempt",
        new=AsyncMock(return_value=make_submit_response()),
    )

    response = client.post(
        "/attempts/1/submit", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["percentage"] == 100.0

    app.dependency_overrides.clear()


def test_submit_attempt_route_already_submitted(client, mocker):
    """
    Test the submit attempt endpoint returns 400 when already submitted.
    """
    from app.exceptions.custom_exceptions import AttemptAlreadySubmittedException

    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.submit_attempt",
        new=AsyncMock(side_effect=AttemptAlreadySubmittedException()),
    )

    response = client.post(
        "/attempts/1/submit", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 400

    app.dependency_overrides.clear()


def test_resume_attempt_route(client, mocker):
    """
    Test the resume attempt endpoint returns 200.
    """
    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.resume_attempt",
        new=AsyncMock(return_value=make_attempt_response()),
    )

    response = client.get(
        "/attempts/1", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == "1"

    app.dependency_overrides.clear()