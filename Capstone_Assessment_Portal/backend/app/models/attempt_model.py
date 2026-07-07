"""
Pydantic model representing a quiz attempt document stored in MongoDB.
"""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AttemptModel(BaseModel):
    """
    Represents a quiz attempt document to be created in the database.

    Stores a locked snapshot of the quiz's questions (including their
    correct answers) at the moment the attempt starts, so that later
    changes to the question bank never affect grading of an attempt
    already in progress. This model intentionally has no id field,
    since MongoDB assigns the _id automatically on insert.
    """

    quiz_id: str
    student_id: str
    attempt_number: int
    questions_snapshot: list[dict]
    answers: dict[str, int] = Field(default_factory=dict)
    status: Literal["in_progress", "submitted", "expired"] = "in_progress"
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    submitted_at: Optional[datetime] = None
    total_questions: Optional[int] = None
    correct_answers: Optional[int] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None