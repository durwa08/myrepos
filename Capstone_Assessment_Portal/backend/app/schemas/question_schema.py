"""
Request and response schemas for question-related APIs.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.constants import (
    INVALID_CORRECT_ANSWER_INDEX_MESSAGE,
    INVALID_OPTIONS_COUNT_MESSAGE,
    MCQ_OPTIONS_COUNT,
    TRUE_FALSE_OPTIONS,
)



class QuestionCreateRequest(BaseModel):
    """
    Request model for creating a question.

    For MCQ questions, exactly 4 options must be provided and
    correct_answer_index must fall within 0-3. For True/False
    questions, options are fixed automatically and
    correct_answer_index must be 0 or 1.
    """

    quiz_id: str
    question_text: str = Field(min_length=5, max_length=500)
    question_type: Literal["mcq", "true_false"]
    options: Optional[list[str]] = None
    correct_answer_index: int
    difficulty: Literal["easy", "medium", "hard"]
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_options_and_answer(self) -> "QuestionCreateRequest":
        """
        Validate that options and correct_answer_index are consistent
        with the question type, and normalize True/False options.
        """
        if self.question_type == "mcq":
            if self.options is None or len(self.options) != MCQ_OPTIONS_COUNT:
                raise ValueError(INVALID_OPTIONS_COUNT_MESSAGE)
            if not 0 <= self.correct_answer_index < MCQ_OPTIONS_COUNT:
                raise ValueError(INVALID_CORRECT_ANSWER_INDEX_MESSAGE)

        if self.question_type == "true_false":
            self.options = TRUE_FALSE_OPTIONS
            if not 0 <= self.correct_answer_index < len(TRUE_FALSE_OPTIONS):
                raise ValueError(INVALID_CORRECT_ANSWER_INDEX_MESSAGE)

        return self


class QuestionUpdateRequest(BaseModel):
    """
    Request model for updating a question.

    All fields are optional to support partial updates. Consistency
    between question_type, options, and correct_answer_index is
    re-validated in the service layer against the existing question,
    since a partial update may only change one of these fields.
    """

    question_text: Optional[str] = Field(default=None, min_length=5, max_length=500)
    question_type: Optional[Literal["mcq", "true_false"]] = None
    options: Optional[list[str]] = None
    correct_answer_index: Optional[int] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    tags: Optional[list[str]] = None


class QuestionResponse(BaseModel):
    """
    Response model containing question details.
    """

    id: str
    quiz_id: str
    question_text: str
    question_type: str
    options: list[str]
    correct_answer_index: int
    difficulty: str
    tags: list[str]
    created_by: str


class QuestionPublicResponse(BaseModel):
    """
    Public-facing question response with the correct answer hidden.

    Used for endpoints accessible to students, so quiz questions can
    be viewed without revealing correct_answer_index ahead of time.
    """

    id: str
    quiz_id: str
    question_text: str
    question_type: str
    options: list[str]
    difficulty: str
    tags: list[str]