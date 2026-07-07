"""
Test cases for question request/response schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.question_schema import (
    QuestionCreateRequest,
    QuestionResponse,
    QuestionUpdateRequest,
)


def test_mcq_question_valid():
    """
    Test a valid MCQ question with exactly 4 options passes validation.
    """
    question = QuestionCreateRequest(
        quiz_id="6a45f4149915f959917d382b",
        question_text="What is the capital of France?",
        question_type="mcq",
        options=["Paris", "London", "Rome", "Berlin"],
        correct_answer_index=0,
        difficulty="easy",
        tags=["geography"],
    )
    assert question.options == ["Paris", "London", "Rome", "Berlin"]
    assert question.correct_answer_index == 0


def test_mcq_question_wrong_options_count():
    """
    Test MCQ question fails when options count is not exactly 4.
    """
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            quiz_id="6a45f4149915f959917d382b",
            question_text="What is the capital of France?",
            question_type="mcq",
            options=["Paris", "London", "Rome"],
            correct_answer_index=0,
            difficulty="easy",
        )


def test_mcq_question_missing_options():
    """
    Test MCQ question fails when options are not provided at all.
    """
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            quiz_id="6a45f4149915f959917d382b",
            question_text="What is the capital of France?",
            question_type="mcq",
            correct_answer_index=0,
            difficulty="easy",
        )


def test_mcq_question_correct_index_out_of_range():
    """
    Test MCQ question fails when correct_answer_index is out of range.
    """
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            quiz_id="6a45f4149915f959917d382b",
            question_text="What is the capital of France?",
            question_type="mcq",
            options=["Paris", "London", "Rome", "Berlin"],
            correct_answer_index=4,
            difficulty="easy",
        )


def test_true_false_question_auto_fills_options():
    """
    Test True/False questions auto-fill options regardless of input.
    """
    question = QuestionCreateRequest(
        quiz_id="6a45f4149915f959917d382b",
        question_text="Python is a compiled language.",
        question_type="true_false",
        correct_answer_index=1,
        difficulty="medium",
    )
    assert question.options == ["True", "False"]
    assert question.correct_answer_index == 1


def test_true_false_question_correct_index_out_of_range():
    """
    Test True/False question fails when correct_answer_index is not 0 or 1.
    """
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            quiz_id="6a45f4149915f959917d382b",
            question_text="Python is a compiled language.",
            question_type="true_false",
            correct_answer_index=2,
            difficulty="medium",
        )


def test_question_text_too_short():
    """
    Test question creation fails when question_text is too short.
    """
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            quiz_id="6a45f4149915f959917d382b",
            question_text="Hi?",
            question_type="true_false",
            correct_answer_index=0,
            difficulty="easy",
        )


def test_question_default_tags_empty_list():
    """
    Test that tags default to an empty list when not provided.
    """
    question = QuestionCreateRequest(
        quiz_id="6a45f4149915f959917d382b",
        question_text="Python is a compiled language.",
        question_type="true_false",
        correct_answer_index=0,
        difficulty="easy",
    )
    assert question.tags == []


def test_question_update_partial():
    """
    Test that a question update payload allows partial fields.
    """
    update = QuestionUpdateRequest(difficulty="hard")
    assert update.difficulty == "hard"
    assert update.question_text is None


def test_question_response_schema():
    """
    Test the response schema holds the expected fields.
    """
    response = QuestionResponse(
        id="1",
        quiz_id="6a45f4149915f959917d382b",
        question_text="What is the capital of France?",
        question_type="mcq",
        options=["Paris", "London", "Rome", "Berlin"],
        correct_answer_index=0,
        difficulty="easy",
        tags=["geography"],
        created_by="durwapahariya08@gmail.com",
    )
    assert response.question_text == "What is the capital of France?"
    assert response.correct_answer_index == 0