"""
Test cases for quiz request/response schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.quiz_schema import (
    QuizCreateRequest,
    QuizResponse,
    QuizUpdateRequest,
)


def test_quiz_create_valid():
    """
    Test a valid quiz creation payload passes schema validation.
    """
    quiz = QuizCreateRequest(
        title="Python Basics",
        description="Covers variables, loops, and functions.",
        category_id="6a45f4149915f959917d382b",
        time_limit_minutes=30,
    )
    assert quiz.title == "Python Basics"
    assert quiz.time_limit_minutes == 30


def test_quiz_create_title_too_short():
    """
    Test quiz creation fails when title is below the minimum length.
    """
    with pytest.raises(ValidationError):
        QuizCreateRequest(
            title="P",
            category_id="6a45f4149915f959917d382b",
            time_limit_minutes=30,
        )


def test_quiz_create_time_limit_zero():
    """
    Test quiz creation fails when time_limit_minutes is zero or below.
    """
    with pytest.raises(ValidationError):
        QuizCreateRequest(
            title="Python Basics",
            category_id="6a45f4149915f959917d382b",
            time_limit_minutes=0,
        )


def test_quiz_create_time_limit_too_high():
    """
    Test quiz creation fails when time_limit_minutes exceeds the maximum.
    """
    with pytest.raises(ValidationError):
        QuizCreateRequest(
            title="Python Basics",
            category_id="6a45f4149915f959917d382b",
            time_limit_minutes=301,
        )


def test_quiz_create_without_description():
    """
    Test quiz creation succeeds without an optional description.
    """
    quiz = QuizCreateRequest(
        title="Python Basics",
        category_id="6a45f4149915f959917d382b",
        time_limit_minutes=30,
    )
    assert quiz.description is None


def test_quiz_update_partial():
    """
    Test that a quiz update payload allows partial fields.
    """
    quiz_update = QuizUpdateRequest(time_limit_minutes=45)
    assert quiz_update.time_limit_minutes == 45
    assert quiz_update.title is None


def test_quiz_response_schema():
    """
    Test the response schema holds the expected fields.
    """
    response = QuizResponse(
        id="1",
        title="Python Basics",
        description="Covers variables, loops, and functions.",
        category_id="6a45f4149915f959917d382b",
        time_limit_minutes=30,
        pass_percentage=40.0,
        created_by="durwapahariya08@gmail.com",
    )
    assert response.title == "Python Basics"
    assert response.time_limit_minutes == 30
    assert response.pass_percentage == 40.0