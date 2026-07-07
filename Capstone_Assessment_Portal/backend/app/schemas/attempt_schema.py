"""
Request and response schemas for quiz attempt APIs.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QuestionSnapshotResponse(BaseModel):
    """
    Public-facing view of a snapshotted question.

    Deliberately excludes correct_answer_index, since this is shown
    to the student while the attempt is in progress.
    """

    question_id: str
    question_text: str
    question_type: str
    options: list[str]
    difficulty: str
    tags: list[str]


class AnswerSaveRequest(BaseModel):
    """
    Request model for saving a single answer mid-attempt.
    """

    question_id: str
    answer_index: int = Field(ge=0)


class AttemptResponse(BaseModel):
    """
    Response model returned when a quiz attempt starts, is resumed, or
    has an answer saved.

    The questions field only ever contains the student-safe view of
    each question — correct answers are never exposed here. The
    answers field reflects whatever the student has saved so far.
    """

    id: str
    quiz_id: str
    attempt_number: int
    status: str
    started_at: datetime
    expires_at: datetime
    questions: list[QuestionSnapshotResponse]
    answers: dict[str, int] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration for datetime JSON serialization."""

        json_encoders = {datetime: lambda dt: dt.isoformat()}


class AnswerBreakdownItem(BaseModel):
    """
    Per-question result shown after an attempt is submitted.
    """

    question_id: str
    question_text: str
    selected_answer_index: Optional[int]
    correct_answer_index: int
    is_correct: bool


class AttemptResultResponse(BaseModel):
    """
    Response model returned after a quiz attempt is submitted.

    Reveals correct answers and a per-question breakdown, since the
    attempt is now finalized.
    """

    id: str
    quiz_id: str
    attempt_number: int
    status: str
    started_at: datetime
    submitted_at: datetime
    total_questions: int
    correct_answers: int
    percentage: float
    passed: bool
    answer_breakdown: list[AnswerBreakdownItem]

    class Config:
        """Pydantic configuration for datetime JSON serialization."""

        json_encoders = {datetime: lambda dt: dt.isoformat()}