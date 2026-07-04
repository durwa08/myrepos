"""
Request and response schemas for category-related APIs.
"""

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    """
    Request model for creating a category.
    """

    name: str = Field(min_length=2, max_length=100)


class CategoryUpdateRequest(BaseModel):
    """
    Request model for updating a category.
    """

    name: str = Field(min_length=2, max_length=100)


class CategoryResponse(BaseModel):
    """
    Response model containing category details.
    """

    id: str
    name: str
    created_by: str

    class Config:
        """Pydantic configuration for ORM attribute support."""

        from_attributes = True