"""
Pydantic model representing a quiz document stored in MongoDB.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class QuizModel(BaseModel):
    """
    Represents a quiz document to be created in the database.

    This model intentionally has no id field, since MongoDB assigns
    the _id automatically on insert.
    """

    title: str
    description: Optional[str] = None
    category_id: str
    time_limit_minutes: int
    pass_percentage: float = 40.0
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))