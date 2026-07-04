"""
Pydantic model representing a question document stored in MongoDB.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class QuestionModel(BaseModel):
    """
    Represents a question document to be created in the database.

    This model intentionally has no id field, since MongoDB assigns
    the _id automatically on insert.
    """

    quiz_id: str
    question_text: str
    question_type: Literal["mcq", "true_false"]
    options: list[str]
    correct_answer_index: int
    difficulty: Literal["easy", "medium", "hard"]
    tags: list[str] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))