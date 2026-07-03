"""
Repository layer for category-related database operations.

This module is responsible for all direct interactions with the
categories collection in MongoDB.
"""

from bson import ObjectId
from bson.errors import InvalidId

from app.config.database import get_database
from app.models.category_model import CategoryModel

database = get_database()
category_collection = database["categories"]


async def get_category_by_name(name: str) -> dict | None:
    """
    Retrieve a category by its name.

    Returns None if no matching category exists.
    """
    return await category_collection.find_one({"name": name})


async def get_category_by_id(category_id: str) -> dict | None:
    """
    Retrieve a category by its MongoDB ObjectId.

    Returns None if the supplied ID is invalid or no category exists.
    """
    try:
        obj_id = ObjectId(category_id)
    except InvalidId:
        return None

    return await category_collection.find_one({"_id": obj_id})


async def create_category(category: CategoryModel) -> dict:
    """
    Create a new category and return the saved document.
    """
    category_dict = category.model_dump()
    result = await category_collection.insert_one(category_dict)

    created_category = await category_collection.find_one(
        {"_id": result.inserted_id}
    )
    return created_category


async def update_category(category_id: str, new_name: str) -> dict | None:
    """
    Update the name of an existing category.

    Returns the updated category or None if the ID is invalid.
    """
    try:
        obj_id = ObjectId(category_id)
    except InvalidId:
        return None

    await category_collection.update_one(
        {"_id": obj_id},
        {"$set": {"name": new_name}},
    )

    updated_category = await category_collection.find_one({"_id": obj_id})
    return updated_category


async def delete_category(category_id: str) -> bool:
    """
    Delete a category by its ID.

    Returns True if a category was deleted, otherwise False.
    """
    try:
        obj_id = ObjectId(category_id)
    except InvalidId:
        return False

    result = await category_collection.delete_one({"_id": obj_id})
    return result.deleted_count > 0


async def list_categories() -> list[dict]:
    """
    Retrieve all categories from the database.
    """
    categories = []

    async for category in category_collection.find():
        categories.append(category)

    return categories


def serialize_category(category: dict) -> dict:
    """
    Convert a MongoDB category document into an API-friendly format.
    """
    return {
        "id": str(category["_id"]),
        "name": category["name"],
        "created_by": category["created_by"],
    }