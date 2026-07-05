"""
Test cases for the quiz repository layer.
"""

from unittest.mock import AsyncMock

import pytest

from app.models.quiz_model import QuizModel
from app.repositories.quiz_repository import (
    create_quiz,
    delete_quiz,
    get_quiz_by_id,
    get_quiz_by_title_and_category,
    list_quizzes,
    serialize_quiz,
    update_quiz,
)


@pytest.mark.asyncio
async def test_get_quiz_by_title_and_category_found(mocker):
    """
    Test that an existing quiz is returned when found by title and category.
    """
    mock_collection = mocker.patch(
        "app.repositories.quiz_repository.quiz_collection"
    )
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await get_quiz_by_title_and_category(
        "Python Basics", "6a45f4149915f959917d382b"
    )

    assert result["title"] == "Python Basics"


@pytest.mark.asyncio
async def test_get_quiz_by_title_and_category_not_found(mocker):
    """
    Test that None is returned when no quiz matches the title and category.
    """
    mock_collection = mocker.patch(
        "app.repositories.quiz_repository.quiz_collection"
    )
    mock_collection.find_one = AsyncMock(return_value=None)

    result = await get_quiz_by_title_and_category(
        "Missing Quiz", "6a45f4149915f959917d382b"
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_quiz_by_id_found(mocker):
    """
    Test that an existing quiz is returned when found by a valid id.
    """
    mock_collection = mocker.patch(
        "app.repositories.quiz_repository.quiz_collection"
    )
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "6a45f4149915f959917d382b",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await get_quiz_by_id("6a45f4149915f959917d382b")

    assert result["title"] == "Python Basics"


@pytest.mark.asyncio
async def test_get_quiz_by_id_invalid_id(mocker):
    """
    Test that None is returned when the id is not a valid ObjectId.
    """
    mocker.patch("app.repositories.quiz_repository.quiz_collection")

    result = await get_quiz_by_id("not-a-valid-id")

    assert result is None


@pytest.mark.asyncio
async def test_create_quiz(mocker):
    """
    Test that a new quiz is inserted and the created document returned.
    """
    mock_collection = mocker.patch(
        "app.repositories.quiz_repository.quiz_collection"
    )

    inserted_result = mocker.Mock()
    inserted_result.inserted_id = "1"
    mock_collection.insert_one = AsyncMock(return_value=inserted_result)
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    new_quiz = QuizModel(
        title="Python Basics",
        category_id="6a45f4149915f959917d382b",
        time_limit_minutes=30,
        created_by="durwapahariya08@gmail.com",
    )

    result = await create_quiz(new_quiz)

    assert result["title"] == "Python Basics"
    mock_collection.insert_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_quiz_valid_id(mocker):
    """
    Test that an existing quiz is updated correctly.
    """
    mock_collection = mocker.patch(
        "app.repositories.quiz_repository.quiz_collection"
    )
    mock_collection.update_one = AsyncMock()
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "6a45f4149915f959917d382b",
            "title": "Advanced Python",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 45,
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await update_quiz(
        "6a45f4149915f959917d382b", {"title": "Advanced Python", "time_limit_minutes": 45}
    )

    assert result["title"] == "Advanced Python"
    mock_collection.update_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_quiz_invalid_id(mocker):
    """
    Test that None is returned when updating with an invalid id.
    """
    mocker.patch("app.repositories.quiz_repository.quiz_collection")

    result = await update_quiz("not-a-valid-id", {"title": "Advanced Python"})

    assert result is None


@pytest.mark.asyncio
async def test_delete_quiz_success(mocker):
    """
    Test that deleting an existing quiz returns True.
    """
    mock_collection = mocker.patch(
        "app.repositories.quiz_repository.quiz_collection"
    )
    delete_result = mocker.Mock()
    delete_result.deleted_count = 1
    mock_collection.delete_one = AsyncMock(return_value=delete_result)

    result = await delete_quiz("6a45f4149915f959917d382b")

    assert result is True


@pytest.mark.asyncio
async def test_delete_quiz_invalid_id(mocker):
    """
    Test that deleting with an invalid id returns False.
    """
    mocker.patch("app.repositories.quiz_repository.quiz_collection")

    result = await delete_quiz("not-a-valid-id")

    assert result is False


@pytest.mark.asyncio
async def test_list_quizzes_no_filter(mocker):
    """
    Test that all quizzes are returned when no category filter is given.
    """
    mock_collection = mocker.patch(
        "app.repositories.quiz_repository.quiz_collection"
    )

    async def fake_cursor():
        yield {
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        }
        yield {
            "_id": "2",
            "title": "Java Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382c",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        }

    mock_collection.find = mocker.Mock(return_value=fake_cursor())

    result = await list_quizzes()

    assert len(result) == 2
    mock_collection.find.assert_called_once_with({})


@pytest.mark.asyncio
async def test_list_quizzes_with_category_filter(mocker):
    """
    Test that quizzes are filtered by category_id when provided.
    """
    mock_collection = mocker.patch(
        "app.repositories.quiz_repository.quiz_collection"
    )

    async def fake_cursor():
        yield {
            "_id": "1",
            "title": "Python Basics",
            "description": None,
            "category_id": "6a45f4149915f959917d382b",
            "time_limit_minutes": 30,
            "created_by": "durwapahariya08@gmail.com",
        }

    mock_collection.find = mocker.Mock(return_value=fake_cursor())

    result = await list_quizzes("6a45f4149915f959917d382b")

    assert len(result) == 1
    mock_collection.find.assert_called_once_with(
        {"category_id": "6a45f4149915f959917d382b"}
    )


def test_serialize_quiz():
    """
    Test that a raw MongoDB quiz document is converted correctly.
    """
    raw_quiz = {
        "_id": "1",
        "title": "Python Basics",
        "description": "Covers basics.",
        "category_id": "6a45f4149915f959917d382b",
        "time_limit_minutes": 30,
        "created_by": "durwapahariya08@gmail.com",
    }

    result = serialize_quiz(raw_quiz)

    assert result["id"] == "1"
    assert result["title"] == "Python Basics"
    assert result["category_id"] == "6a45f4149915f959917d382b"