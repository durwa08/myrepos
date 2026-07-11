"""
Test cases for quiz attempt routes.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

from app.main import app
from app.middleware.auth_middleware import require_admin, require_student
from app.schemas.attempt_schema import (
    AnswerBreakdownItem,
    AttemptResponse,
    AttemptResultResponse,
    QuestionSnapshotResponse,
    ResultHistoryItem,
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


def make_result_response():
    """
    Build a sample AttemptResultResponse for mocking service return values.
    """
    return AttemptResultResponse(
        id="1",
        quiz_id="quiz1",
        attempt_number=1,
        status="submitted",
        started_at=NOW,
        submitted_at=NOW,
        total_questions=1,
        correct_answers=1,
        percentage=100.0,
        passed=True,
        answer_breakdown=[
            AnswerBreakdownItem(
                question_id="q1",
                question_text="What is 2+2?",
                selected_answer_index=2,
                correct_answer_index=2,
                is_correct=True,
            )
        ],
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
    Test the submit attempt endpoint returns 200 with the score.
    """
    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.submit_attempt",
        new=AsyncMock(return_value=make_result_response()),
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


def test_get_attempt_result_route(client, mocker):
    """
    Test the get result endpoint returns 200 with the full breakdown.
    """
    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.get_result",
        new=AsyncMock(return_value=make_result_response()),
    )

    response = client.get(
        "/attempts/1/result", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["passed"] is True

    app.dependency_overrides.clear()


def test_get_attempt_result_route_access_denied(client, mocker):
    """
    Test the get result endpoint returns 403 for a non-owning student.
    """
    from app.exceptions.custom_exceptions import AttemptAccessDeniedException

    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.get_result",
        new=AsyncMock(side_effect=AttemptAccessDeniedException()),
    )

    response = client.get(
        "/attempts/1/result", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()


def test_get_my_history_route(client, mocker):
    """
    Test the student history endpoint returns 200 with a list.
    """
    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.get_history",
        new=AsyncMock(
            return_value=[
                ResultHistoryItem(
                    id="1",
                    quiz_id="quiz1",
                    student_id="student1",
                    attempt_number=1,
                    total_questions=1,
                    correct_answers=1,
                    percentage=100.0,
                    passed=True,
                    submitted_at=NOW,
                )
            ]
        ),
    )

    response = client.get(
        "/attempts/history/me", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    app.dependency_overrides.clear()


def test_get_admin_dashboard_route_as_admin(client, mocker):
    """
    Test the admin dashboard endpoint returns 200 for an admin.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "admin1",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.attempt_routes.AttemptService.get_admin_dashboard",
        new=AsyncMock(
            return_value=[
                ResultHistoryItem(
                    id="1",
                    quiz_id="quiz1",
                    student_id="student1",
                    attempt_number=1,
                    total_questions=1,
                    correct_answers=1,
                    percentage=100.0,
                    passed=True,
                    submitted_at=NOW,
                )
            ]
        ),
    )

    response = client.get(
        "/attempts/admin/dashboard", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    app.dependency_overrides.clear()


def test_get_admin_dashboard_route_without_admin_token(client):
    """
    Test the admin dashboard endpoint returns 401/403 without admin auth.
    """
    response = client.get("/attempts/admin/dashboard")

    assert response.status_code in (401, 403)