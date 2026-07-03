"""
Pydantic model representing a category document stored in MongoDB.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """
    Represents a category document to be created in the database.

    This model intentionally has no id field, since MongoDB assigns
    the _id automatically on insert.
    """

    name: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))