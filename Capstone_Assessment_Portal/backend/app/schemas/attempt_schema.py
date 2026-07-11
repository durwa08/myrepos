"""
Request and response schemas for quiz attempt APIs.
"""

from datetime import datetime

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


class SubmitAttemptResponse(BaseModel):
    """
    Response model returned immediately after submitting an attempt.

    Provides the score summary at the moment of submission. For
    viewing this result again later (with full answer breakdown),
    use the Result module's GET /results/{attempt_id} endpoint.
    """

    id: str
    quiz_id: str
    attempt_number: int
    status: str
    submitted_at: datetime
    total_questions: int
    correct_answers: int
    percentage: float
    passed: bool

    class Config:
        """Pydantic configuration for datetime JSON serialization."""

        json_encoders = {datetime: lambda dt: dt.isoformat()}