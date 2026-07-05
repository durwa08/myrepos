"""
Test cases for QuestionService.
"""

from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    QuestionAlreadyExistsException,
    QuestionNotFoundException,
    QuizNotFoundException,
)
from app.schemas.question_schema import QuestionCreateRequest, QuestionUpdateRequest
from app.services.question_service import QuestionService


@pytest.mark.asyncio
async def test_create_question_success(mocker):
    """
    Test successful question creation when quiz exists and text is unique.
    """
    mocker.patch(
        "app.services.question_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={"_id": "6a45f4149915f959917d382b", "title": "Python Basics"},
    )
    mocker.patch(
        "app.services.question_service.get_question_by_text_and_quiz",
        new_callable=AsyncMock,
        return_value=None,
    )
    mocker.patch(
        "app.services.question_service.create_question",
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

    service = QuestionService()
    request = QuestionCreateRequest(
        quiz_id="6a45f4149915f959917d382b",
        question_text="What is the capital of France?",
        question_type="mcq",
        options=["Paris", "London", "Rome", "Berlin"],
        correct_answer_index=0,
        difficulty="easy",
    )

    response = await service.create_question(
        request, admin_id="durwapahariya08@gmail.com"
    )

    assert response.question_text == "What is the capital of France?"


@pytest.mark.asyncio
async def test_create_question_quiz_not_found(mocker):
    """
    Test question creation fails when the quiz does not exist.
    """
    mocker.patch(
        "app.services.question_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = QuestionService()
    request = QuestionCreateRequest(
        quiz_id="missing_quiz",
        question_text="What is the capital of France?",
        question_type="mcq",
        options=["Paris", "London", "Rome", "Berlin"],
        correct_answer_index=0,
        difficulty="easy",
    )

    with pytest.raises(QuizNotFoundException):
        await service.create_question(request, admin_id="durwapahariya08@gmail.com")


@pytest.mark.asyncio
async def test_create_question_duplicate_text(mocker):
    """
    Test question creation fails when the text already exists in the quiz.
    """
    mocker.patch(
        "app.services.question_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={"_id": "6a45f4149915f959917d382b", "title": "Python Basics"},
    )
    mocker.patch(
        "app.services.question_service.get_question_by_text_and_quiz",
        new_callable=AsyncMock,
        return_value={"question_text": "What is the capital of France?"},
    )

    service = QuestionService()
    request = QuestionCreateRequest(
        quiz_id="6a45f4149915f959917d382b",
        question_text="What is the capital of France?",
        question_type="mcq",
        options=["Paris", "London", "Rome", "Berlin"],
        correct_answer_index=0,
        difficulty="easy",
    )

    with pytest.raises(QuestionAlreadyExistsException):
        await service.create_question(request, admin_id="durwapahariya08@gmail.com")


@pytest.mark.asyncio
async def test_get_questions_by_quiz_success(mocker):
    """
    Test retrieving all questions for a valid quiz.
    """
    mocker.patch(
        "app.services.question_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value={"_id": "6a45f4149915f959917d382b", "title": "Python Basics"},
    )
    mocker.patch(
        "app.services.question_service.list_questions_by_quiz",
        new_callable=AsyncMock,
        return_value=[
            {
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
        ],
    )

    service = QuestionService()
    result = await service.get_questions_by_quiz("6a45f4149915f959917d382b")

    assert len(result) == 1
    assert result[0].question_text == "What is the capital of France?"


@pytest.mark.asyncio
async def test_get_questions_by_quiz_quiz_not_found(mocker):
    """
    Test retrieving questions fails when the quiz does not exist.
    """
    mocker.patch(
        "app.services.question_service.get_quiz_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = QuestionService()

    with pytest.raises(QuizNotFoundException):
        await service.get_questions_by_quiz("missing_quiz")


@pytest.mark.asyncio
async def test_get_question_success(mocker):
    """
    Test retrieving a single question by id.
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

    service = QuestionService()
    result = await service.get_question("1")

    assert result.question_text == "What is the capital of France?"


@pytest.mark.asyncio
async def test_get_question_not_found(mocker):
    """
    Test retrieving a question fails when it does not exist.
    """
    mocker.patch(
        "app.services.question_service.get_question_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = QuestionService()

    with pytest.raises(QuestionNotFoundException):
        await service.get_question("missing_id")


@pytest.mark.asyncio
async def test_update_question_success(mocker):
    """
    Test successful question update when the question exists.
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
    mocker.patch(
        "app.services.question_service.update_question",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "What is the capital of France?",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "hard",
            "tags": [],
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    service = QuestionService()
    request = QuestionUpdateRequest(difficulty="hard")

    response = await service.update_question("1", request)

    assert response.difficulty == "hard"


@pytest.mark.asyncio
async def test_update_question_not_found(mocker):
    """
    Test question update fails when the question does not exist.
    """
    mocker.patch(
        "app.services.question_service.get_question_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = QuestionService()
    request = QuestionUpdateRequest(difficulty="hard")

    with pytest.raises(QuestionNotFoundException):
        await service.update_question("missing_id", request)


@pytest.mark.asyncio
async def test_update_question_mcq_invalid_options_count(mocker):
    """
    Test question update fails when changing to MCQ with wrong option count.
    """
    mocker.patch(
        "app.services.question_service.get_question_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "Python is a compiled language.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer_index": 0,
            "difficulty": "easy",
            "tags": [],
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    service = QuestionService()
    request = QuestionUpdateRequest(
        question_type="mcq", options=["A", "B"]
    )

    with pytest.raises(ValueError):
        await service.update_question("1", request)


@pytest.mark.asyncio
async def test_update_question_duplicate_text(mocker):
    """
    Test question update fails when new text duplicates another question
    in the same quiz.
    """
    mocker.patch(
        "app.services.question_service.get_question_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "quiz_id": "6a45f4149915f959917d382b",
            "question_text": "Old question text here",
            "question_type": "mcq",
            "options": ["Paris", "London", "Rome", "Berlin"],
            "correct_answer_index": 0,
            "difficulty": "easy",
            "tags": [],
            "created_by": "durwapahariya08@gmail.com",
        },
    )
    mocker.patch(
        "app.services.question_service.get_question_by_text_and_quiz",
        new_callable=AsyncMock,
        return_value={"_id": "2", "question_text": "Duplicate text here"},
    )

    service = QuestionService()
    request = QuestionUpdateRequest(question_text="Duplicate text here")

    with pytest.raises(QuestionAlreadyExistsException):
        await service.update_question("1", request)


@pytest.mark.asyncio
async def test_delete_question_success(mocker):
    """
    Test successful question deletion.
    """
    mocker.patch(
        "app.services.question_service.delete_question",
        new_callable=AsyncMock,
        return_value=True,
    )

    service = QuestionService()
    result = await service.delete_question("1")

    assert result is None


@pytest.mark.asyncio
async def test_delete_question_not_found(mocker):
    """
    Test question deletion fails when the question does not exist.
    """
    mocker.patch(
        "app.services.question_service.delete_question",
        new_callable=AsyncMock,
        return_value=False,
    )

    service = QuestionService()

    with pytest.raises(QuestionNotFoundException):
        await service.delete_question("missing_id")