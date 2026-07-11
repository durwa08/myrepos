"""
Test cases for result routes.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.main import app
from app.middleware.auth_middleware import require_admin, require_student
from app.schemas.result_schema import (
    AnswerBreakdownItem,
    AttemptResultResponse,
    ResultHistoryItem,
)

NOW = datetime.now(timezone.utc)


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


def test_get_attempt_result_route(client, mocker):
    """
    Test the get result endpoint returns 200 with the full breakdown.
    """
    app.dependency_overrides[require_student] = lambda: {
        "sub": "student1",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.result_routes.ResultService.get_result",
        new=AsyncMock(return_value=make_result_response()),
    )

    response = client.get(
        "/results/1", headers={"Authorization": "Bearer fake_token"}
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
        "app.api.v1.result_routes.ResultService.get_result",
        new=AsyncMock(side_effect=AttemptAccessDeniedException()),
    )

    response = client.get(
        "/results/1", headers={"Authorization": "Bearer fake_token"}
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
        "app.api.v1.result_routes.ResultService.get_history",
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
        "/results/history/me", headers={"Authorization": "Bearer fake_token"}
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
        "app.api.v1.result_routes.ResultService.get_admin_dashboard",
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
        "/results/admin/dashboard", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    app.dependency_overrides.clear()


def test_get_admin_dashboard_route_without_admin_token(client):
    """
    Test the admin dashboard endpoint returns 401/403 without admin auth.
    """
    response = client.get("/results/admin/dashboard")

    assert response.status_code in (401, 403)