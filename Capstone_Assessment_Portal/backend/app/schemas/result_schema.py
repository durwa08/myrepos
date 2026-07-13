"""
Response schemas for result viewing APIs.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnswerBreakdownItem(BaseModel):
    """
    Per-question result shown after an attempt is submitted.
    """

    question_id: str
    question_text: str
    options: list[str]
    selected_answer_index: Optional[int]
    correct_answer_index: int
    is_correct: bool


class AttemptResultResponse(BaseModel):
    """
    Response model returned when viewing a submitted attempt's result.

    Reveals correct answers and a per-question breakdown, since the
    attempt is finalized.
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


class ResultHistoryItem(BaseModel):
    """
    Lightweight summary of a submitted attempt, used in history and
    admin dashboard listings.
    """

    id: str
    quiz_id: str
    student_id: str
    attempt_number: int
    total_questions: int
    correct_answers: int
    percentage: float
    passed: bool
    submitted_at: datetime

    class Config:
        """Pydantic configuration for datetime JSON serialization."""

        json_encoders = {datetime: lambda dt: dt.isoformat()}