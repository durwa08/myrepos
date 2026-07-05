"""
Test cases for QuizService.
"""

from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    CategoryNotFoundException,
    QuizAlreadyExistsException,
    QuizNotFoundException,
)
from app.schemas.quiz_schema import QuizCreateRequest, QuizUpdateRequest
from app.services.quiz_service import QuizService


@pytest.mark.asyncio
async def test_create_quiz_success(mocker):
    """
    Test successful quiz creation when category exists and title is unique.
    """
    mocker.patch(
        "app.services.quiz_service.get_category_by_id",
        new_callable=AsyncMock,
        return_value={"_id": "6a45f4149915f959917d382b", "name": "Python"},
    )
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_title_and_category",
        new_callable=AsyncMock,
        return_value=None,
    )
    mocker.patch(
        "app.services.quiz_service.create_quiz",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    service = QuizService()
    request = QuizCreateRequest(
        title="Python Basics",
        category_id="6a45f4149915f959917d382b",
        time_limit_minutes=30,
    )

    response = await service.create_quiz(request, admin_id="durwapahariya08@gmail.com")

    assert response.title == "Python Basics"


@pytest.mark.asyncio
async def test_create_quiz_invalid_category(mocker):
    """
    Test quiz creation fails when the category does not exist.
    """
    mocker.patch(
        "app.services.quiz_service.get_category_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = QuizService()
    request = QuizCreateRequest(
        title="Python Basics",
        category_id="missing_category",
        time_limit_minutes=30,
    )

    with pytest.raises(CategoryNotFoundException):
        await service.create_quiz(request, admin_id="durwapahariya08@gmail.com")


@pytest.mark.asyncio
async def test_create_quiz_duplicate_title(mocker):
    """
    Test quiz creation fails when the title already exists in the category.
    """
    mocker.patch(
        "app.services.quiz_service.get_category_by_id",
        new_callable=AsyncMock,
        return_value={"_id": "6a45f4149915f959917d382b", "name": "Python"},
    )
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_title_and_category",
        new_callable=AsyncMock,
        return_value={"title": "Python Basics"},
    )

    service = QuizService()
    request = QuizCreateRequest(
        title="Python Basics",
        category_id="6a45f4149915f959917d382b",
        time_limit_minutes=30,
    )

    with pytest.raises(QuizAlreadyExistsException):
        await service.create_quiz(request, admin_id="durwapahariya08@gmail.com")


@pytest.mark.asyncio
async def test_get_all_quizzes(mocker):
    """
    Test that all quizzes are retrieved and returned.
    """
    mocker.patch(
        "app.services.quiz_service.list_quizzes",
        new_callable=AsyncMock,
        return_value=[
            {
                "_id": "1",
                "title": "Python Basics",
                "description": None,
                "category_id": "6a45f4149915f959917d382b",
                "time_limit_minutes": 30,
                "created_by": "durwapahariya08@gmail.com",
            }
        ],
    )

    service = QuizService()
    result = await service.get_all_quizzes()

    assert len(result) == 1
    assert result[0].title == "Python Basics"


@pytest.mark.asyncio
async def test_get_quiz_success(mocker):
    """
    Test retrieving a single quiz by id.
    """
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    service = QuizService()
    result = await service.get_quiz("1")

    assert result.title == "Python Basics"


@pytest.mark.asyncio
async def test_get_quiz_not_found(mocker):
    """
    Test retrieving a quiz fails when it does not exist.
    """
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = QuizService()

    with pytest.raises(QuizNotFoundException):
        await service.get_quiz("missing_id")


@pytest.mark.asyncio
async def test_update_quiz_success(mocker):
    """
    Test successful quiz update when the quiz exists.
    """
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        },
    )
    mocker.patch(
        "app.services.quiz_service.update_quiz",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "title": "Advanced Python",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 45,
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    service = QuizService()
    request = QuizUpdateRequest(title="Advanced Python", time_limit_minutes=45)

    response = await service.update_quiz("1", request)

    assert response.title == "Advanced Python"


@pytest.mark.asyncio
async def test_update_quiz_not_found(mocker):
    """
    Test quiz update fails when the quiz does not exist.
    """
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = QuizService()
    request = QuizUpdateRequest(title="Advanced Python")

    with pytest.raises(QuizNotFoundException):
        await service.update_quiz("missing_id", request)


@pytest.mark.asyncio
async def test_update_quiz_invalid_category(mocker):
    """
    Test quiz update fails when changing to a non-existent category.
    """
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        },
    )
    mocker.patch(
        "app.services.quiz_service.get_category_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = QuizService()
    request = QuizUpdateRequest(category_id="missing_category")

    with pytest.raises(CategoryNotFoundException):
        await service.update_quiz("1", request)


@pytest.mark.asyncio
async def test_delete_quiz_success(mocker):
    """
    Test successful quiz deletion.
    """
    mocker.patch(
        "app.services.quiz_service.delete_quiz",
        new_callable=AsyncMock,
        return_value=True,
    )

    service = QuizService()
    result = await service.delete_quiz("1")

    assert result is None


@pytest.mark.asyncio
async def test_delete_quiz_not_found(mocker):
    """
    Test quiz deletion fails when the quiz does not exist.
    """
    mocker.patch(
        "app.services.quiz_service.delete_quiz",
        new_callable=AsyncMock,
        return_value=False,
    )

    service = QuizService()

    with pytest.raises(QuizNotFoundException):
        await service.delete_quiz("missing_id")

@pytest.mark.asyncio
async def test_update_quiz_duplicate_title(mocker):
    """
    Test quiz update fails when renaming to a title that already exists
    in the same category on a different quiz.
    """
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        },
    )
    mocker.patch(
        "app.services.quiz_service.get_quiz_by_title_and_category",
        new_callable=AsyncMock,
        return_value={
            "_id": "2",
            "title": "Advanced Python",
            "category_id": "6a45f4149915f959917d382b",
        },
    )

    service = QuizService()
    request = QuizUpdateRequest(title="Advanced Python")

    with pytest.raises(QuizAlreadyExistsException):
        await service.update_quiz("1", request)        