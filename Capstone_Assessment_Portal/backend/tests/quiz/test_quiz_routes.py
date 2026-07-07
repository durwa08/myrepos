"""
Test cases for quiz routes.
"""

from unittest.mock import AsyncMock

from app.main import app
from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.common_schema import MessageResponse
from app.schemas.quiz_schema import QuizResponse


def test_create_quiz_route_as_admin(client, mocker):
    """
    Test the create quiz endpoint returns 201 for an admin user.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.quiz_routes.QuizService.create_quiz",
        new=AsyncMock(
            return_value=QuizResponse(
                id="1",
                title="Python Basics",
                description=None,
                category_id="6a45f4149915f959917d382b",
                time_limit_minutes=30,
                pass_percentage=40.0,
                created_by="durwapahariya08@gmail.com",
            )
        ),
    )

    response = client.post(
        "/quizzes",
        json={
            "title": "Python Basics",
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
        },
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Python Basics"

    app.dependency_overrides.clear()


def test_create_quiz_route_category_not_found(client, mocker):
    """
    Test the create quiz endpoint returns 404 for an invalid category.
    """
    from app.exceptions.custom_exceptions import CategoryNotFoundException

    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.quiz_routes.QuizService.create_quiz",
        new=AsyncMock(side_effect=CategoryNotFoundException()),
    )

    response = client.post(
        "/quizzes",
        json={
            "title": "Python Basics",
            "category_id": "missing_category",
            "time_limit_minutes": 30,
        },
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_list_quizzes_route(client, mocker):
    """
    Test the list quizzes endpoint returns 200 with a list.
    """
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.quiz_routes.QuizService.get_all_quizzes",
        new=AsyncMock(
            return_value=[
                QuizResponse(
                    id="1",
                    title="Python Basics",
                    description=None,
                    category_id="6a45f4149915f959917d382b",
                    time_limit_minutes=30,
                    pass_percentage=40.0,
                    created_by="durwapahariya08@gmail.com",
                )
            ]
        ),
    )

    response = client.get(
        "/quizzes", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Python Basics"

    app.dependency_overrides.clear()


def test_get_quiz_route(client, mocker):
    """
    Test the get single quiz endpoint returns 200.
    """
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.quiz_routes.QuizService.get_quiz",
        new=AsyncMock(
            return_value=QuizResponse(
                id="1",
                title="Python Basics",
                description=None,
                category_id="6a45f4149915f959917d382b",
                time_limit_minutes=30,
                pass_percentage=40.0,
                created_by="durwapahariya08@gmail.com",
            )
        ),
    )

    response = client.get(
        "/quizzes/1", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == "1"

    app.dependency_overrides.clear()


def test_get_quiz_route_not_found(client, mocker):
    """
    Test the get single quiz endpoint returns 404 when missing.
    """
    from app.exceptions.custom_exceptions import QuizNotFoundException

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.quiz_routes.QuizService.get_quiz",
        new=AsyncMock(side_effect=QuizNotFoundException()),
    )

    response = client.get(
        "/quizzes/missing_id", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_update_quiz_route_as_admin(client, mocker):
    """
    Test the update quiz endpoint returns 200 for an admin user.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.quiz_routes.QuizService.update_quiz",
        new=AsyncMock(
            return_value=QuizResponse(
                id="1",
                title="Advanced Python",
                description=None,
                category_id="6a45f4149915f959917d382b",
                time_limit_minutes=45,
                pass_percentage=40.0,
                created_by="durwapahariya08@gmail.com",
            )
        ),
    )

    response = client.put(
        "/quizzes/1",
        json={"title": "Advanced Python", "time_limit_minutes": 45},
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Advanced Python"

    app.dependency_overrides.clear()


def test_delete_quiz_route_as_admin(client, mocker):
    """
    Test the delete quiz endpoint returns 200 with a success message.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.quiz_routes.QuizService.delete_quiz",
        new=AsyncMock(
            return_value=MessageResponse(message="Quiz deleted successfully.")
        ),
    )

    response = client.delete(
        "/quizzes/1", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Quiz deleted successfully."

    app.dependency_overrides.clear()


def test_create_quiz_route_without_admin_token(client):
    """
    Test the create quiz endpoint returns 401/403 without admin auth.
    """
    response = client.post(
        "/quizzes",
        json={
            "title": "Python Basics",
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
        },
    )

    assert response.status_code in (401, 403)