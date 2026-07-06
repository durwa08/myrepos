"""
Test cases for question routes.
"""

from unittest.mock import AsyncMock

from app.main import app
from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.question_schema import QuestionResponse
from app.schemas.common_schema import MessageResponse

def test_create_question_route_as_admin(client, mocker):
    """
    Test the create question endpoint returns 201 for an admin user.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.question_routes.QuestionService.create_question",
        new=AsyncMock(
            return_value=QuestionResponse(
                id="1",
                quiz_id="6a45f4149915f959917d382b",
                question_text="What is the capital of France?",
                question_type="mcq",
                options=["Paris", "London", "Rome", "Berlin"],
                correct_answer_index=0,
                difficulty="easy",
                tags=[],
                created_by="durwapahariya08@gmail.com",
            )
        ),
    )

    response = client.post(
        "/questions",
        json={
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "easy",
        },
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 201
    assert response.json()["question_text"] == "What is the capital of France?"

    app.dependency_overrides.clear()


def test_create_question_route_quiz_not_found(client, mocker):
    """
    Test the create question endpoint returns 404 for an invalid quiz.
    """
    from app.exceptions.custom_exceptions import QuizNotFoundException

    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.question_routes.QuestionService.create_question",
        new=AsyncMock(side_effect=QuizNotFoundException()),
    )

    response = client.post(
        "/questions",
        json={
            "quiz_id": "missing_quiz",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "easy",
        },
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_get_questions_by_quiz_route(client, mocker):
    """
    Test the get questions by quiz endpoint returns 200 with a list.
    """
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.question_routes.QuestionService.get_questions_by_quiz",
        new=AsyncMock(
            return_value=[
                QuestionResponse(
                    id="1",
                    quiz_id="6a45f4149915f959917d382b",
                    question_text="What is the capital of France?",
                    question_type="mcq",
                    options=["Paris", "London", "Rome", "Berlin"],
                    correct_answer_index=0,
                    difficulty="easy",
                    tags=[],
                    created_by="durwapahariya08@gmail.com",
                )
            ]
        ),
    )

    response = client.get(
        "/questions/quiz/6a45f4149915f959917d382b",
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 200
    assert response.json()[0]["question_text"] == "What is the capital of France?"

    app.dependency_overrides.clear()


def test_get_question_route(client, mocker):
    """
    Test the get single question endpoint returns 200.
    """
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.question_routes.QuestionService.get_question",
        new=AsyncMock(
            return_value=QuestionResponse(
                id="1",
                quiz_id="6a45f4149915f959917d382b",
                question_text="What is the capital of France?",
                question_type="mcq",
                options=["Paris", "London", "Rome", "Berlin"],
                correct_answer_index=0,
                difficulty="easy",
                tags=[],
                created_by="durwapahariya08@gmail.com",
            )
        ),
    )

    response = client.get(
        "/questions/1", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == "1"

    app.dependency_overrides.clear()


def test_get_question_route_not_found(client, mocker):
    """
    Test the get single question endpoint returns 404 when missing.
    """
    from app.exceptions.custom_exceptions import QuestionNotFoundException

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    mocker.patch(
        "app.api.v1.question_routes.QuestionService.get_question",
        new=AsyncMock(side_effect=QuestionNotFoundException()),
    )

    response = client.get(
        "/questions/missing_id", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_update_question_route_as_admin(client, mocker):
    """
    Test the update question endpoint returns 200 for an admin user.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.question_routes.QuestionService.update_question",
        new=AsyncMock(
            return_value=QuestionResponse(
                id="1",
                quiz_id="6a45f4149915f959917d382b",
                question_text="What is the capital of France?",
                question_type="mcq",
                options=["Paris", "London", "Rome", "Berlin"],
                correct_answer_index=0,
                difficulty="hard",
                tags=[],
                created_by="durwapahariya08@gmail.com",
            )
        ),
    )

    response = client.put(
        "/questions/1",
        json={"difficulty": "hard"},
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 200
    assert response.json()["difficulty"] == "hard"

    app.dependency_overrides.clear()


def test_delete_question_route_as_admin(client, mocker):
    """
    Test the delete question endpoint returns 200 with a success message.
    """
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "durwapahariya08@gmail.com",
        "role": "admin",
    }

    mocker.patch(
        "app.api.v1.question_routes.QuestionService.delete_question",
        new=AsyncMock(
            return_value=MessageResponse(message="Question deleted successfully.")
        ),
    )

    response = client.delete(
        "/questions/1", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Question deleted successfully."

    app.dependency_overrides.clear()


def test_create_question_route_without_admin_token(client):
    """
    Test the create question endpoint returns 401/403 without admin auth.
    """
    response = client.post(
        "/questions",
        json={
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "easy",
        },
    )

    assert response.status_code in (401, 403)


def test_get_question_route_hides_correct_answer(client, mocker):
    """
    Test that the get single question endpoint response never contains
    correct_answer_index, even though the underlying document has it.
    """
    mocker.patch(
        "app.services.question_service.get_question_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "easy",
            "tags": [],
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "durwa08@gmail.com",
        "role": "student",
    }

    response = client.get(
        "/questions/1", headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    assert "correct_answer_index" not in response.json()

    app.dependency_overrides.clear()    