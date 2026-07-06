"""
Request and response schemas for quiz-related APIs.
"""

from typing import Optional

from pydantic import BaseModel, Field


class QuizCreateRequest(BaseModel):
    """
    Request model for creating a quiz.
    """

    title: str = Field(min_length=2, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)
    category_id: str
    time_limit_minutes: int = Field(gt=0, le=300)


class QuizUpdateRequest(BaseModel):
    """
    Request model for updating a quiz.

    All fields are optional to support partial updates.
    """

    title: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)
    category_id: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(default=None, gt=0, le=300)


class QuizResponse(BaseModel):
    """
    Response model containing quiz details.
    """

    id: str
    title: str
    description: Optional[str] = None
    category_id: str
    time_limit_minutes: int
    created_by: str

    class Config:
        """Pydantic configuration for ORM attribute support."""

        from_attributes = True