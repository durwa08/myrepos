"""
Test cases for category request/response schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.category_schema import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)


def test_category_create_valid():
    """
    Test a valid category creation payload passes schema validation.
    """
    category = CategoryCreateRequest(name="Python")
    assert category.name == "Python"


def test_category_create_name_too_short():
    """
    Test category creation fails when name is below the minimum length.
    """
    with pytest.raises(ValidationError):
        CategoryCreateRequest(name="P")


def test_category_create_name_too_long():
    """
    Test category creation fails when name exceeds the maximum length.
    """
    with pytest.raises(ValidationError):
        CategoryCreateRequest(name="P" * 101)


def test_category_update_valid():
    """
    Test a valid category update payload passes schema validation.
    """
    category = CategoryUpdateRequest(name="Python")
    assert category.name == "Python"


def test_category_update_name_too_short():
    """
    Test category update fails when name is below the minimum length.
    """
    with pytest.raises(ValidationError):
        CategoryUpdateRequest(name="P")


def test_category_response_schema():
    """
    Test the response schema holds the expected fields.
    """
    response = CategoryResponse(
        id="1",
        name="Python",
        created_by="durwapahariya08@gmail.com",
    )
    assert response.id == "1"
    assert response.name == "Python"
    assert response.created_by == "durwapahariya08@gmail.com"