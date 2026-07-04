"""
Pydantic model representing a quiz document stored in MongoDB.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class QuizModel(BaseModel):
    """
    Represents a quiz document in the database.
    """

    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    description: Optional[str] = None
    category_id: str
    time_limit_minutes: int
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        """Pydantic configuration for MongoDB field mapping."""

        populate_by_name = True