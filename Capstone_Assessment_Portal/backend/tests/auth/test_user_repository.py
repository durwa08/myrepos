"""
Test cases for the user repository layer.
"""

from unittest.mock import AsyncMock

import pytest

from app.models.user_model import UserModel
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    serialize_user,
)


@pytest.mark.asyncio
async def test_get_user_by_email_found(mocker):
    """
    Test that an existing user is returned when found by email.
    """
    mock_collection = mocker.patch(
        "app.repositories.user_repository.user_collection"
    )
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "1",
            "username": "durwa08",
            "email": "durwa08@gmail.com",
            "hashed_password": "hashed_password",
            "role": "student",
        }
    )

    result = await get_user_by_email("durwa08@gmail.com")

    assert result["email"] == "durwa08@gmail.com"
    mock_collection.find_one.assert_awaited_once_with(
        {"email": "durwa08@gmail.com"}
    )


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(mocker):
    """
    Test that None is returned when no user matches the email.
    """
    mock_collection = mocker.patch(
        "app.repositories.user_repository.user_collection"
    )
    mock_collection.find_one = AsyncMock(return_value=None)

    result = await get_user_by_email("missing@gmail.com")

    assert result is None


@pytest.mark.asyncio
async def test_create_user(mocker):
    """
    Test that a new user is inserted and the created document returned.
    """
    mock_collection = mocker.patch(
        "app.repositories.user_repository.user_collection"
    )

    inserted_result = mocker.Mock()
    inserted_result.inserted_id = "1"
    mock_collection.insert_one = AsyncMock(return_value=inserted_result)
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": "1",
            "username": "durwa08",
            "email": "durwa08@gmail.com",
            "hashed_password": "hashed_password",
            "role": "student",
        }
    )

    new_user = UserModel(
        username="durwa08",
        email="durwa08@gmail.com",
        hashed_password="hashed_password",
        role="student",
    )

    result = await create_user(new_user)

    assert result["email"] == "durwa08@gmail.com"
    mock_collection.insert_one.assert_awaited_once()
    mock_collection.find_one.assert_awaited_once_with({"_id": "1"})


def test_serialize_user():
    """
    Test that a raw MongoDB user document is converted correctly.
    """
    raw_user = {
        "_id": "1",
        "username": "durwa08",
        "email": "durwa08@gmail.com",
        "hashed_password": "hashed_password",
        "role": "student",
    }

    result = serialize_user(raw_user)

    assert result["id"] == "1"
    assert result["username"] == "durwa08"
    assert result["email"] == "durwa08@gmail.com"
    assert result["role"] == "student"
    assert "hashed_password" not in result