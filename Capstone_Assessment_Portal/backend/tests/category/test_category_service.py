"""
Test cases for CategoryService.
"""

from unittest.mock import AsyncMock

import pytest

from app.exceptions.custom_exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
)
from app.schemas.category_schema import CategoryCreateRequest, CategoryUpdateRequest
from app.services.category_service import CategoryService


@pytest.mark.asyncio
async def test_create_category_success(mocker):
    """
    Test successful category creation when the name is not already taken.
    """
    mocker.patch(
        "app.services.category_service.get_category_by_name",
        new_callable=AsyncMock,
        return_value=None,
    )
    mocker.patch(
        "app.services.category_service.create_category",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "name": "Python",
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    service = CategoryService()
    request = CategoryCreateRequest(name="Python")

    response = await service.create_category(
        request, admin_id="durwapahariya08@gmail.com"
    )

    assert response.name == "Python"
    assert response.created_by == "durwapahariya08@gmail.com"


@pytest.mark.asyncio
async def test_create_category_duplicate_name(mocker):
    """
    Test category creation fails when the name already exists.
    """
    mocker.patch(
        "app.services.category_service.get_category_by_name",
        new_callable=AsyncMock,
        return_value={"name": "Python"},
    )

    service = CategoryService()
    request = CategoryCreateRequest(name="Python")

    with pytest.raises(CategoryAlreadyExistsException):
        await service.create_category(
            request, admin_id="durwapahariya08@gmail.com"
        )


@pytest.mark.asyncio
async def test_get_all_categories(mocker):
    """
    Test that all categories are retrieved and returned.
    """
    mocker.patch(
        "app.services.category_service.list_categories",
        new_callable=AsyncMock,
        return_value=[
            {"_id": "1", "name": "Python", "created_by": "durwapahariya08@gmail.com"},
            {"_id": "2", "name": "Java", "created_by": "durwapahariya08@gmail.com"},
        ],
    )

    service = CategoryService()
    result = await service.get_all_categories()

    assert len(result) == 2
    assert result[0].name == "Python"


@pytest.mark.asyncio
async def test_update_category_success(mocker):
    """
    Test successful category update when the category exists.
    """
    mocker.patch(
        "app.services.category_service.get_category_by_id",
        new_callable=AsyncMock,
        return_value={"_id": "1", "name": "Python", "created_by": "durwapahariya08@gmail.com"},
    )
    mocker.patch(
        "app.services.category_service.update_category",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "name": "Advanced Python",
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    service = CategoryService()
    request = CategoryUpdateRequest(name="Advanced Python")

    response = await service.update_category("1", request)

    assert response.name == "Advanced Python"


@pytest.mark.asyncio
async def test_update_category_not_found(mocker):
    """
    Test category update fails when the category does not exist.
    """
    mocker.patch(
        "app.services.category_service.get_category_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = CategoryService()
    request = CategoryUpdateRequest(name="Advanced Python")

    with pytest.raises(CategoryNotFoundException):
        await service.update_category("missing_id", request)


@pytest.mark.asyncio
async def test_delete_category_success(mocker):
    """
    Test successful category deletion.
    """
    mocker.patch(
        "app.services.category_service.delete_category",
        new_callable=AsyncMock,
        return_value=True,
    )

    service = CategoryService()
    result = await service.delete_category("1")

    assert result.message == "Category deleted successfully."


@pytest.mark.asyncio
async def test_delete_category_not_found(mocker):
    """
    Test category deletion fails when the category does not exist.
    """
    mocker.patch(
        "app.services.category_service.delete_category",
        new_callable=AsyncMock,
        return_value=False,
    )

    service = CategoryService()

    with pytest.raises(CategoryNotFoundException):
        await service.delete_category("missing_id")

@pytest.mark.asyncio
async def test_get_category_by_id_success(mocker):
    """
    Test retrieving a single category by its id.
    """
    mocker.patch(
        "app.services.category_service.get_category_by_id",
        new_callable=AsyncMock,
        return_value={
            "_id": "1",
            "name": "Python",
            "created_by": "durwapahariya08@gmail.com",
        },
    )

    service = CategoryService()
    result = await service.get_category_by_id("1")

    assert result.name == "Python"


@pytest.mark.asyncio
async def test_get_category_by_id_not_found(mocker):
    """
    Test retrieving a category fails when it does not exist.
    """
    mocker.patch(
        "app.services.category_service.get_category_by_id",
        new_callable=AsyncMock,
        return_value=None,
    )

    service = CategoryService()

    with pytest.raises(CategoryNotFoundException):
        await service.get_category_by_id("missing_id")        