"""
Request and response schemas for quiz attempt APIs.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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


class AttemptResponse(BaseModel):
    """
    Response model returned when a quiz attempt starts.

    The questions field only ever contains the student-safe view of
    each question — correct answers are never exposed here.
    """

    id: str
    quiz_id: str
    attempt_number: int
    status: str
    started_at: datetime
    expires_at: datetime
    questions: list[QuestionSnapshotResponse]

    class Config:
        """Pydantic configuration for datetime JSON serialization."""

        json_encoders = {datetime: lambda dt: dt.isoformat()}