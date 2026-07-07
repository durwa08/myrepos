"""
Test cases for the question repository layer.
"""

from unittest.mock import AsyncMock
from app.exceptions.custom_exceptions import QuestionAlreadyExistsException

import pytest

from app.models.question_model import QuestionModel
from app.repositories.question_repository import (
    create_question,
    delete_question,
    get_question_by_id,
    get_question_by_text_and_quiz,
    list_questions_by_quiz,
    serialize_question,
    update_question,
)


@pytest.mark.asyncio
async def test_get_question_by_text_and_quiz_found(mocker):
    """
    Test that an existing question is returned when found by text and quiz.
    """
    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "1",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "easy",
            "tags": ["geography"],
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await get_question_by_text_and_quiz(
        "What is the capital of France?", "6a45f4149915f959917d382b"
    )

    assert result["question_text"] == "What is the capital of France?"


@pytest.mark.asyncio
async def test_get_question_by_text_and_quiz_not_found(mocker):
    """
    Test that None is returned when no question matches the text and quiz.
    """
    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )
    mock_collection.find_one = AsyncMock(return_value=None)

    result = await get_question_by_text_and_quiz(
        "Missing question?", "6a45f4149915f959917d382b"
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_question_by_id_found(mocker):
    """
    Test that an existing question is returned when found by a valid id.
    """
    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "6a45f4149915f959917d382b",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "easy",
            "tags": [],
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await get_question_by_id("6a45f4149915f959917d382b")

    assert result["question_text"] == "What is the capital of France?"


@pytest.mark.asyncio
async def test_get_question_by_id_invalid_id(mocker):
    """
    Test that None is returned when the id is not a valid ObjectId.
    """
    mocker.patch("app.repositories.question_repository.question_collection")

    result = await get_question_by_id("not-a-valid-id")

    assert result is None


@pytest.mark.asyncio
async def test_create_question(mocker):
    """
    Test that a new question is inserted and the created document returned.
    """
    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )

    inserted_result = mocker.Mock()
    inserted_result.inserted_id = "1"
    mock_collection.insert_one = AsyncMock(return_value=inserted_result)
    mock_collection.find_one = AsyncMock(
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
        }
    )

    new_question = QuestionModel(
        quiz_id="6a45f4149915f959917d382b",
        question_text="What is the capital of France?",
        question_type="mcq",
        options=["Paris", "London", "Rome", "Berlin"],
        correct_answer_index=0,
        difficulty="easy",
        tags=[],
        created_by="durwapahariya08@gmail.com",
    )

    result = await create_question(new_question)

    assert result["question_text"] == "What is the capital of France?"
    mock_collection.insert_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_question_valid_id(mocker):
    """
    Test that an existing question is updated correctly.
    """
    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )
    mock_collection.update_one = AsyncMock()
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "6a45f4149915f959917d382b",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "hard",
            "tags": [],
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await update_question(
        "6a45f4149915f959917d382b", {"difficulty": "hard"}
    )

    assert result["difficulty"] == "hard"
    mock_collection.update_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_question_invalid_id(mocker):
    """
    Test that None is returned when updating with an invalid id.
    """
    mocker.patch("app.repositories.question_repository.question_collection")

    result = await update_question("not-a-valid-id", {"difficulty": "hard"})

    assert result is None


@pytest.mark.asyncio
async def test_delete_question_success(mocker):
    """
    Test that deleting an existing question returns True.
    """
    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )
    delete_result = mocker.Mock()
    delete_result.deleted_count = 1
    mock_collection.delete_one = AsyncMock(return_value=delete_result)

    result = await delete_question("6a45f4149915f959917d382b")

    assert result is True


@pytest.mark.asyncio
async def test_delete_question_invalid_id(mocker):
    """
    Test that deleting with an invalid id returns False.
    """
    mocker.patch("app.repositories.question_repository.question_collection")

    result = await delete_question("not-a-valid-id")

    assert result is False


@pytest.mark.asyncio
async def test_list_questions_by_quiz(mocker):
    """
    Test that all questions for a specific quiz are returned.
    """
    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )

    async def fake_cursor():
        yield {
            "_id": "1",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "easy",
            "tags": [],
            "created_by": "durwapahariya08@gmail.com",
        }
        yield {
            "_id": "2",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "Python is a compiled language.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer_index": 1,
            "difficulty": "medium",
            "tags": [],
            "created_by": "durwapahariya08@gmail.com",
        }

    mock_collection.find = mocker.Mock(return_value=fake_cursor())

    result = await list_questions_by_quiz("6a45f4149915f959917d382b")

    assert len(result) == 2
    mock_collection.find.assert_called_once_with(
        {"quiz_id": "6a45f4149915f959917d382b"}
    )


def test_serialize_question():
    """
    Test that a raw MongoDB question document is converted correctly.
    """
    raw_question = {
        "_id": "1",
        "quiz_id": "6a45f4149915f959917d382b",
        "question_text": "What is the capital of France?",
        "question_type": "mcq",
        "options": ["Paris", "London", "Rome", "Berlin"],
        "correct_answer_index": 0,
        "difficulty": "easy",
        "tags": ["geography"],
        "created_by": "durwapahariya08@gmail.com",
    }

    result = serialize_question(raw_question)

    assert result["id"] == "1"
    assert result["question_text"] == "What is the capital of France?"
    assert result["tags"] == ["geography"]

@pytest.mark.asyncio
async def test_create_question_duplicate_key_error(mocker):
    """
    Test that a DuplicateKeyError from MongoDB is converted into
    QuestionAlreadyExistsException.
    """
    from pymongo.errors import DuplicateKeyError

    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )
    mock_collection.insert_one = AsyncMock(
        side_effect=DuplicateKeyError("duplicate key")
    )

    new_question = QuestionModel(
        quiz_id="6a45f4149915f959917d382b",
        question_text="What is the capital of France?",
        question_type="mcq",
        options=["Paris", "London", "Rome", "Berlin"],
        correct_answer_index=0,
        difficulty="easy",
        tags=[],
        created_by="durwapahariya08@gmail.com",
    )

    with pytest.raises(QuestionAlreadyExistsException):
        await create_question(new_question)


@pytest.mark.asyncio
async def test_update_question_duplicate_key_error(mocker):
    """
    Test that a DuplicateKeyError from MongoDB during update is converted
    into QuestionAlreadyExistsException.
    """
    from pymongo.errors import DuplicateKeyError

    mock_collection = mocker.patch(
        "app.repositories.question_repository.question_collection"
    )
    mock_collection.update_one = AsyncMock(
        side_effect=DuplicateKeyError("duplicate key")
    )

    with pytest.raises(QuestionAlreadyExistsException):
        await update_question(
            "6a45f4149915f959917d382b", {"question_text": "Duplicate text"}
        )    