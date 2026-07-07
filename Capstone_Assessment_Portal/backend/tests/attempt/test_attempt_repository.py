"""
Test cases for the quiz attempt repository layer.
"""

from unittest.mock import AsyncMock

import pytest

from app.models.attempt_model import AttemptModel
from app.repositories.attempt_repository import (
    count_attempts_by_student_and_quiz,
    create_attempt,
    get_active_attempt,
    get_attempt_by_id,
    list_all_submitted_attempts,
    list_submitted_attempts_by_student,
    mark_attempt_expired,
    save_answer,
    serialize_attempt,
    serialize_result_summary,
    submit_attempt,
)

VALID_ID = "6a45f4149915f959917d382b"


def make_raw_attempt(**overrides):
    """
    Build a raw attempt document dict for use in mocked repository
    return values, with sensible defaults.
    """
    base = {
        "_id": VALID_ID,
        "quiz_id": "quiz1",
        "student_id": "student1",
        "attempt_number": 1,
        "questions_snapshot": [
            {
                "question_id": "q1",
                "question_text": "What is 2+2?",
                "question_type": "mcq",
                "options": ["2", "3", "4", "5"],
                "correct_answer_index": 2,
                "difficulty": "easy",
                "tags": [],
            }
        ],
        "answers": {},
        "status": "in_progress",
        "started_at": "2026-01-01T00:00:00+00:00",
        "expires_at": "2026-01-01T00:30:00+00:00",
        "submitted_at": None,
        "total_questions": None,
        "correct_answers": None,
        "percentage": None,
        "passed": None,
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_count_attempts_by_student_and_quiz(mocker):
    """
    Test counting attempts for a student and quiz.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )
    mock_collection.count_documents = AsyncMock(return_value=2)

    result = await count_attempts_by_student_and_quiz("student1", "quiz1")

    assert result == 2
    mock_collection.count_documents.assert_awaited_once_with(
        {"student_id": "student1", "quiz_id": "quiz1"}
    )


@pytest.mark.asyncio
async def test_get_attempt_by_id_found(mocker):
    """
    Test retrieving an attempt by a valid id.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )
    mock_collection.find_one = AsyncMock(return_value=make_raw_attempt())

    result = await get_attempt_by_id(VALID_ID)

    assert result["quiz_id"] == "quiz1"


@pytest.mark.asyncio
async def test_get_attempt_by_id_invalid_id(mocker):
    """
    Test that an invalid id returns None.
    """
    mocker.patch("app.repositories.attempt_repository.attempt_collection")

    result = await get_attempt_by_id("not-a-valid-id")

    assert result is None


@pytest.mark.asyncio
async def test_get_active_attempt_found(mocker):
    """
    Test retrieving a student's active in-progress attempt for a quiz.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )
    mock_collection.find_one = AsyncMock(return_value=make_raw_attempt())

    result = await get_active_attempt("student1", "quiz1")

    assert result["status"] == "in_progress"
    mock_collection.find_one.assert_awaited_once_with(
        {"student_id": "student1", "quiz_id": "quiz1", "status": "in_progress"}
    )


@pytest.mark.asyncio
async def test_get_active_attempt_not_found(mocker):
    """
    Test that None is returned when there's no active attempt.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )
    mock_collection.find_one = AsyncMock(return_value=None)

    result = await get_active_attempt("student1", "quiz1")

    assert result is None


@pytest.mark.asyncio
async def test_create_attempt(mocker):
    """
    Test creating a new attempt and retrieving the saved document.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )

    inserted_result = mocker.Mock()
    inserted_result.inserted_id = VALID_ID
    mock_collection.insert_one = AsyncMock(return_value=inserted_result)
    mock_collection.find_one = AsyncMock(return_value=make_raw_attempt())

    new_attempt = AttemptModel(
        quiz_id="quiz1",
        student_id="student1",
        attempt_number=1,
        questions_snapshot=[
            {
                "question_id": "q1",
                "question_text": "What is 2+2?",
                "question_type": "mcq",
                "options": ["2", "3", "4", "5"],
                "correct_answer_index": 2,
                "difficulty": "easy",
                "tags": [],
            }
        ],
        expires_at="2026-01-01T00:30:00+00:00",
    )

    result = await create_attempt(new_attempt)

    assert result["quiz_id"] == "quiz1"
    mock_collection.insert_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_answer_valid_id(mocker):
    """
    Test saving an answer updates the attempt's answers map.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )
    mock_collection.update_one = AsyncMock()
    mock_collection.find_one = AsyncMock(
        return_value=make_raw_attempt(answers={"q1": 2})
    )

    result = await save_answer(VALID_ID, "q1", 2)

    assert result["answers"] == {"q1": 2}
    mock_collection.update_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_answer_invalid_id(mocker):
    """
    Test that saving an answer with an invalid id returns None.
    """
    mocker.patch("app.repositories.attempt_repository.attempt_collection")

    result = await save_answer("not-a-valid-id", "q1", 2)

    assert result is None


@pytest.mark.asyncio
async def test_mark_attempt_expired(mocker):
    """
    Test marking an attempt as expired.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )
    mock_collection.update_one = AsyncMock()

    await mark_attempt_expired(VALID_ID)

    mock_collection.update_one.assert_awaited_once_with(
        {"_id": mocker.ANY}, {"$set": {"status": "expired"}}
    )


@pytest.mark.asyncio
async def test_mark_attempt_expired_invalid_id_does_not_raise(mocker):
    """
    Test that marking an invalid id as expired does not raise.
    """
    mocker.patch("app.repositories.attempt_repository.attempt_collection")

    await mark_attempt_expired("not-a-valid-id")


@pytest.mark.asyncio
async def test_submit_attempt(mocker):
    """
    Test submitting an attempt updates it with score data.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )
    mock_collection.update_one = AsyncMock()
    mock_collection.find_one = AsyncMock(
        return_value=make_raw_attempt(
            status="submitted",
            total_questions=1,
            correct_answers=1,
            percentage=100.0,
            passed=True,
        )
    )

    result = await submit_attempt(
        VALID_ID,
        {
            "status": "submitted",
            "total_questions": 1,
            "correct_answers": 1,
            "percentage": 100.0,
            "passed": True,
        },
    )

    assert result["status"] == "submitted"
    assert result["percentage"] == 100.0


@pytest.mark.asyncio
async def test_submit_attempt_invalid_id(mocker):
    """
    Test that submitting with an invalid id returns None.
    """
    mocker.patch("app.repositories.attempt_repository.attempt_collection")

    result = await submit_attempt("not-a-valid-id", {"status": "submitted"})

    assert result is None


@pytest.mark.asyncio
async def test_list_submitted_attempts_by_student(mocker):
    """
    Test listing all submitted attempts for a student.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )

    async def fake_cursor():
        yield make_raw_attempt(status="submitted")

    mock_cursor = mocker.Mock()
    mock_cursor.sort = mocker.Mock(return_value=fake_cursor())
    mock_collection.find = mocker.Mock(return_value=mock_cursor)

    result = await list_submitted_attempts_by_student("student1")

    assert len(result) == 1
    mock_collection.find.assert_called_once_with(
        {"student_id": "student1", "status": "submitted"}
    )


@pytest.mark.asyncio
async def test_list_all_submitted_attempts(mocker):
    """
    Test listing all submitted attempts across every student.
    """
    mock_collection = mocker.patch(
        "app.repositories.attempt_repository.attempt_collection"
    )

    async def fake_cursor():
        yield make_raw_attempt(status="submitted", student_id="student1")
        yield make_raw_attempt(status="submitted", student_id="student2")

    mock_cursor = mocker.Mock()
    mock_cursor.sort = mocker.Mock(return_value=fake_cursor())
    mock_collection.find = mocker.Mock(return_value=mock_cursor)

    result = await list_all_submitted_attempts()

    assert len(result) == 2
    mock_collection.find.assert_called_once_with({"status": "submitted"})


def test_serialize_attempt():
    """
    Test that a raw attempt document is converted into the API-friendly
    format, stripping correct_answer_index from each question.
    """
    raw = make_raw_attempt(answers={"q1": 2})

    result = serialize_attempt(raw)

    assert result["id"] == VALID_ID
    assert result["answers"] == {"q1": 2}
    assert "correct_answer_index" not in result["questions"][0]
    assert result["questions"][0]["question_id"] == "q1"


def test_serialize_result_summary():
    """
    Test that a submitted attempt document is converted into a result
    summary.
    """
    raw = make_raw_attempt(
        status="submitted",
        total_questions=1,
        correct_answers=1,
        percentage=100.0,
        passed=True,
        submitted_at="2026-01-01T00:20:00+00:00",
    )

    result = serialize_result_summary(raw)

    assert result["id"] == VALID_ID
    assert result["percentage"] == 100.0
    assert result["passed"] is True