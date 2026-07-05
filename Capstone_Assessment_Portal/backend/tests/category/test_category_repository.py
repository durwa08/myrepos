"""
Test cases for the category repository layer.
"""

from unittest.mock import AsyncMock

import pytest

from app.models.category_model import CategoryModel
from app.repositories.category_repository import (
    create_category,
    delete_category,
    get_category_by_id,
    get_category_by_name,
    list_categories,
    serialize_category,
    update_category,
)


@pytest.mark.asyncio
async def test_get_category_by_name_found(mocker):
    """
    Test that an existing category is returned when found by name.
    """
    mock_collection = mocker.patch(
        "app.repositories.category_repository.category_collection"
    )
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "1",
            "name": "Python",
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await get_category_by_name("Python")

    assert result["name"] == "Python"
    mock_collection.find_one.assert_awaited_once_with({"name": "Python"})


@pytest.mark.asyncio
async def test_get_category_by_name_not_found(mocker):
    """
    Test that None is returned when no category matches the name.
    """
    mock_collection = mocker.patch(
        "app.repositories.category_repository.category_collection"
    )
    mock_collection.find_one = AsyncMock(return_value=None)

    result = await get_category_by_name("Missing")

    assert result is None


@pytest.mark.asyncio
async def test_get_category_by_id_found(mocker):
    """
    Test that an existing category is returned when found by a valid id.
    """
    mock_collection = mocker.patch(
        "app.repositories.category_repository.category_collection"
    )
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "6a45f4149915f959917d382b",
            "name": "Python",
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await get_category_by_id("6a45f4149915f959917d382b")

    assert result["name"] == "Python"


@pytest.mark.asyncio
async def test_get_category_by_id_invalid_id(mocker):
    """
    Test that None is returned when the id is not a valid ObjectId.
    """
    mocker.patch("app.repositories.category_repository.category_collection")

    result = await get_category_by_id("not-a-valid-id")

    assert result is None


@pytest.mark.asyncio
async def test_create_category(mocker):
    """
    Test that a new category is inserted and the created document returned.
    """
    mock_collection = mocker.patch(
        "app.repositories.category_repository.category_collection"
    )

    inserted_result = mocker.Mock()
    inserted_result.inserted_id = "1"
    mock_collection.insert_one = AsyncMock(return_value=inserted_result)
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "1",
            "name": "Python",
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    new_category = CategoryModel(
        name="Python",
        created_by="durwapahariya08@gmail.com",
    )

    result = await create_category(new_category)

    assert result["name"] == "Python"
    mock_collection.insert_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_category_valid_id(mocker):
    """
    Test that an existing category's name is updated correctly.
    """
    mock_collection = mocker.patch(
        "app.repositories.category_repository.category_collection"
    )
    mock_collection.update_one = AsyncMock()
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "6a45f4149915f959917d382b",
            "name": "Advanced Python",
            "created_by": "durwapahariya08@gmail.com",
        }
    )

    result = await update_category("6a45f4149915f959917d382b", "Advanced Python")

    assert result["name"] == "Advanced Python"
    mock_collection.update_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_category_invalid_id(mocker):
    """
    Test that None is returned when updating with an invalid id.
    """
    mocker.patch("app.repositories.category_repository.category_collection")

    result = await update_category("not-a-valid-id", "Advanced Python")

    assert result is None


@pytest.mark.asyncio
async def test_delete_category_success(mocker):
    """
    Test that deleting an existing category returns True.
    """
    mock_collection = mocker.patch(
        "app.repositories.category_repository.category_collection"
    )
    delete_result = mocker.Mock()
    delete_result.deleted_count = 1
    mock_collection.delete_one = AsyncMock(return_value=delete_result)

    result = await delete_category("6a45f4149915f959917d382b")

    assert result is True


@pytest.mark.asyncio
async def test_delete_category_invalid_id(mocker):
    """
    Test that deleting with an invalid id returns False.
    """
    mocker.patch("app.repositories.category_repository.category_collection")

    result = await delete_category("not-a-valid-id")

    assert result is False


@pytest.mark.asyncio
async def test_list_categories(mocker):
    """
    Test that all categories are returned as a list.
    """
    mock_collection = mocker.patch(
        "app.repositories.category_repository.category_collection"
    )

    async def fake_cursor():
        yield {"_id": "1", "name": "Python", "created_by": "durwapahariya08@gmail.com"}
        yield {"_id": "2", "name": "Java", "created_by": "durwapahariya08@gmail.com"}

    mock_collection.find = mocker.Mock(return_value=fake_cursor())

    result = await list_categories()

    assert len(result) == 2
    assert result[0]["name"] == "Python"


def test_serialize_category():
    """
    Test that a raw MongoDB category document is converted correctly.
    """
    raw_category = {
        "_id": "1",
        "name": "Python",
        "created_by": "durwapahariya08@gmail.com",
    }

    result = serialize_category(raw_category)

    assert result["id"] == "1"
    assert result["name"] == "Python"
    assert result["created_by"] == "durwapahariya08@gmail.com"