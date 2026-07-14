import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.v1.result_routes import (
    get_result_service,
    require_admin,
    require_student,
)


class MockResultService:
    """Mock implementation of ResultService."""

    async def get_history(self, student_id: str):
        return [
            {
                "id": "attempt123",
                "quiz_id": "quiz123",
                "student_id": student_id,
                "attempt_number": 1,
                "total_questions": 10,
                "correct_answers": 8,
                "percentage": 80.0,
                "passed": True,
                "submitted_at": "2026-07-14T10:00:00",
            }
        ]

    async def get_admin_dashboard(self):
        return [
            {
                "id": "attempt123",
                "quiz_id": "quiz123",
                "student_id": "student123",
                "attempt_number": 1,
                "total_questions": 10,
                "correct_answers": 8,
                "percentage": 80.0,
                "passed": True,
                "submitted_at": "2026-07-14T10:00:00",
            }
        ]

    async def get_result(self, attempt_id: str, student_id: str):
        return {
            "id": attempt_id,
            "quiz_id": "quiz123",
            "attempt_number": 1,
            "status": "submitted",
            "started_at": "2026-07-14T09:45:00",
            "submitted_at": "2026-07-14T10:00:00",
            "total_questions": 10,
            "correct_answers": 8,
            "percentage": 80.0,
            "passed": True,
            "answer_breakdown": [
                {
                    "question_id": "q1",
                    "question_text": "What is 2 + 2?",
                    "options": ["1", "2", "3", "4"],
                    "selected_answer_index": 3,
                    "correct_answer_index": 3,
                    "is_correct": True,
                }
            ],
        }


@pytest.fixture
async def async_client():
    """Provide an asynchronous HTTP client for testing."""

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_get_my_history(async_client):
    """Test retrieving the authenticated student's result history."""

    app.dependency_overrides[get_result_service] = lambda: MockResultService()
    app.dependency_overrides[require_student] = (
        lambda: {"sub": "student@test.com"}
    )

    response = await async_client.get("/results/history/me")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_admin_dashboard(async_client):
    """Test retrieving the administrator dashboard."""

    app.dependency_overrides[get_result_service] = lambda: MockResultService()
    app.dependency_overrides[require_admin] = (
        lambda: {"sub": "admin@test.com"}
    )

    response = await async_client.get("/results/admin/dashboard")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_attempt_result(async_client):
    """Test retrieving a submitted attempt result."""

    app.dependency_overrides[get_result_service] = lambda: MockResultService()
    app.dependency_overrides[require_student] = (
        lambda: {"sub": "student@test.com"}
    )

    response = await async_client.get("/results/attempt123")

    assert response.status_code == 200
    assert response.json()["id"] == "attempt123"

    app.dependency_overrides.clear()